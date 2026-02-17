<?php
declare(strict_types=1);

/*
 * /ku/server/forum_latest.php
 * PHP 7.x compatible.
 */

ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');
error_reporting(E_ALL);

header('Content-Type: text/plain; charset=utf-8');

$rssUrl = 'https://kuforum.ru/forums/opyt-kontrolja-upotreblenija-alkogolja-lichnye-temy.3/index.rss';
$outFile = __DIR__ . '/../forum/latest.json';
$logFile = __DIR__ . '/../forum/latest_debug.log';
$cacheTtlSeconds = 600;
$maxItems = 7;

function ku_log(string $msg, string $logFile): void
{
  @mkdir(dirname($logFile), 0755, true);
  @file_put_contents($logFile, date('Y-m-d H:i:s') . ' ' . $msg . "\n", FILE_APPEND);
}

function ku_force_utf8_xml_decl(string $xmlStr): string
{
  $xmlStr = preg_replace('/<\?xml\s+version="1\.0"\s+encoding="[^"]*"\s*\?>/i', '<?xml version="1.0" encoding="UTF-8"?>', $xmlStr, 1);
  $xmlStr = preg_replace("/<\?xml\s+version='1\.0'\s+encoding='[^']*'\s*\?>/i", "<?xml version='1.0' encoding='UTF-8'?>", $xmlStr, 1);
  return $xmlStr;
}

function ku_is_valid_utf8(string $s): bool
{
  return (bool) @preg_match('//u', $s);
}

/*
 * исправляет mojibake вида "РќРµР№..." -> "Ней..."
 * логика:
 * - строка $s в UTF-8 содержит символы "Р", "С" и т.п.;
 * - если перекодировать эту строку в Windows-1251, получатся байты исходного UTF-8;
 * - эти байты уже являются корректным UTF-8, их и нужно оставить.
 */
function ku_unmojibake(string $s): string
{
  $bytes = @iconv('UTF-8', 'Windows-1251//IGNORE', $s);
  if ($bytes !== false && $bytes !== '' && ku_is_valid_utf8($bytes)) {
    return $bytes;
  }
  return $s;
}

function ku_to_utf8(string $s): string
{
  // 1) убрать мусорные байты в пределах UTF-8
  $clean = @iconv('UTF-8', 'UTF-8//IGNORE', $s);
  if ($clean !== false) {
    $s = $clean;
  }

  // 2) попытка распутать mojibake 1–2 прохода
  $s2 = ku_unmojibake($s);
  if ($s2 !== $s) {
    $s = $s2;
    $s3 = ku_unmojibake($s); // на случай двойной порчи
    if ($s3 !== $s) {
      $s = $s3;
    }
  }

  // 3) финальная очистка
  $clean2 = @iconv('UTF-8', 'UTF-8//IGNORE', $s);
  if ($clean2 !== false) {
    $s = $clean2;
  }

  return $s;
}


function ku_utf8ize_array(array $arr): array
{
  foreach ($arr as $k => $v) {
    if (is_string($v)) {
      $arr[$k] = ku_to_utf8($v);
    } elseif (is_array($v)) {
      $arr[$k] = ku_utf8ize_array($v);
    }
  }
  return $arr;
}

ku_log('start', $logFile);
ku_log('rss: ' . $rssUrl, $logFile);
ku_log('out: ' . $outFile, $logFile);

@mkdir(dirname($outFile), 0755, true);

$force = isset($_GET['force']) && $_GET['force'] === '1';

if (file_exists($outFile) && !$force) {
  $age = time() - filemtime($outFile);
  if ($age < $cacheTtlSeconds) {
    echo "OK (cached)\n";
    ku_log('ok cached age=' . $age, $logFile);
    exit;
  }
}


$context = stream_context_create([
  'http' => [
    'method' => 'GET',
    'timeout' => 12,
    'header' => "User-Agent: KU-site-rss-fetcher/1.0\r\n"
  ]
]);

$xmlStr = @file_get_contents($rssUrl, false, $context);
if ($xmlStr === false || trim($xmlStr) === '') {
  $err = error_get_last();
  ku_log('fetch rss failed: ' . ($err['message'] ?? 'unknown'), $logFile);
  http_response_code(502);
  echo "ERROR: cannot fetch RSS\n";
  exit;
}

ku_log('rss bytes: ' . strlen($xmlStr), $logFile);

$xmlStr = ku_force_utf8_xml_decl($xmlStr);

libxml_use_internal_errors(true);
$xml = simplexml_load_string($xmlStr);
if ($xml === false) {
  ku_log('xml parse failed', $logFile);
  foreach (libxml_get_errors() as $e) {
    ku_log('libxml: ' . trim($e->message), $logFile);
  }
  http_response_code(502);
  echo "ERROR: invalid RSS XML\n";
  exit;
}

$items = [];
if (isset($xml->channel->item)) {
  foreach ($xml->channel->item as $item) {
    $title = trim((string)$item->title);
    $link = trim((string)$item->link);
    $pubDate = trim((string)$item->pubDate);

    $title = ku_to_utf8($title);

    if ($link !== '' && substr($link, 0, 1) === '/') {
      $link = 'https://kuforum.ru' . $link;
    }

    $dateText = $pubDate;
    $ts = strtotime($pubDate);
    if ($ts !== false) {
      $dateText = date('Y-m-d H:i', $ts);
    }

    if ($title !== '' && $link !== '') {
      $items[] = [
        'title' => $title,
        'url' => $link,
        'dateText' => $dateText
      ];
    }

    if (count($items) >= $maxItems) {
      break;
    }
  }
}

ku_log('items: ' . count($items), $logFile);

if (count($items) === 0) {
  http_response_code(502);
  echo "ERROR: no items in RSS\n";
  exit;
}

$items = ku_utf8ize_array($items);

$json = json_encode($items, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
if ($json === false) {
  ku_log('json failed: ' . json_last_error_msg(), $logFile);
  http_response_code(500);
  echo "ERROR: json encode failed: " . json_last_error_msg() . "\n";
  exit;
}

$tmpFile = $outFile . '.tmp';
$w = file_put_contents($tmpFile, $json);
if ($w === false) {
  ku_log('write tmp failed', $logFile);
  http_response_code(500);
  echo "ERROR: cannot write tmp file\n";
  exit;
}

if (!@rename($tmpFile, $outFile)) {
  $err = error_get_last();
  ku_log('rename failed: ' . ($err['message'] ?? 'unknown'), $logFile);
  http_response_code(500);
  echo "ERROR: cannot move tmp file\n";
  exit;
}

ku_log('ok updated', $logFile);
echo "OK (updated)\n";
