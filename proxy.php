<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: application/json; charset=utf-8');

$api_key = 'j8P-v6j199uEynnYd9sL217vWfsGpA0K';
$base    = 'https://kuforum.ru/api';

function xf_get($url, $api_key) {
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'XF-Api-Key: ' . $api_key,
        'XF-Api-User: 1',
    ]);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response, true);
}

// Берём 20 тем, сортируем по last_post_date
$data = xf_get($base . '/threads?page=1&limit=20&order=last_post_date&direction=desc', $api_key);
$threads = $data['threads'] ?? [];

// Сортируем по last_post_date убыванию (на всякий случай)
usort($threads, function($a, $b) {
    return $b['last_post_date'] - $a['last_post_date'];
});

$result = [];
$count  = 0;

foreach ($threads as $thread) {
    if ($count >= 4) break;

    $post_id   = $thread['last_post_id'];
    $post_data = xf_get($base . '/posts/' . $post_id, $api_key);

    $text = '';
    if (!empty($post_data['post']['message_parsed'])) {
        $text = strip_tags($post_data['post']['message_parsed']);
    } elseif (!empty($post_data['post']['message'])) {
        $text = $post_data['post']['message'];
    }
    $text = trim(preg_replace('/\s+/', ' ', $text));
    if (mb_strlen($text) > 150) $text = mb_substr($text, 0, 150) . '…';

    // Пропускаем пустые посты
    if ($text === '') continue;

    $result[] = [
        'title'    => $thread['title'],
        'url'      => $thread['view_url'],
        'post_url' => 'https://kuforum.ru/posts/' . $post_id . '/',
        'author'   => $thread['last_post_username'],
        'date'     => $thread['last_post_date'],
        'snippet'  => $text,
    ];

    $count++;
}

echo json_encode($result, JSON_UNESCAPED_UNICODE);
