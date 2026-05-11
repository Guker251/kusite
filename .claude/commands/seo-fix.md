Запусти полный SEO-аудит и воркфлоу для alkonorm.ru.
Проект: /Users/guker/Desktop/ku

## Шаг 1 — Получить свежие исключённые страницы из Яндекса

python3 /Users/guker/Desktop/ku/scripts/fetch_excluded.py

Скрипт обновит /docs/seo/excluded-registry.md.

## Шаг 2 — Технические проверки (один раз за сессию)

### robots.txt (/Users/guker/Desktop/ku/robots.txt)
- Есть ли Disallow для: /articles/faq/, /articles/karta-sayta/, /articles/knigi/, /articles/stati/
- Sitemap указывает на https://alkonorm.ru/sitemap.xml

### sitemap.xml (/Users/guker/Desktop/ku/sitemap.xml)
- Нет сервисных страниц (stategiya-ku, testy, test-*.html, uchet-*, *-ku.html и подобных)
- Нет 301-редиректов (*.html-версий страниц с директорным каноником)
- Все задеплоенные контентные страницы присутствуют

### noindex на сервисных страницах
Все файлы со статусом service в реестре должны иметь <meta name="robots" content="noindex, nofollow">
Проверка: grep -rL "noindex" /Users/guker/Desktop/ku/articles/*.html | grep -v "7-shagov-ku-za"

### canonical = og:url = BreadcrumbList last item
Запустить проверку Python-скриптом по всем *.html и index.html в /articles/.
При несовпадении — исправить все три значения в файле.

### .htaccess (/Users/guker/Desktop/ku/.htaccess)
- /index.html → https://alkonorm.ru/
- RewriteRule для index.html в поддиректориях использует https://

При любом изменении файла — задеплоить:
curl -T "<локальный путь>" "ftp://shared-26.smartape.ru/alkonorm.ru/<путь от корня>" --user "$ALKONORM_FTP_USER:$ALKONORM_FTP_PASS"

## Шаг 3 — Обработка контентных страниц из реестра

Взять из /docs/seo/excluded-registry.md все строки: status=todo, category=content.
Для каждой страницы по очереди:

1. Найти блок в docs/semantic-core.yaml по URL (не читать файл целиком)
2. Прочитать HTML-файл страницы
3. Проверить критичные проблемы:
   - title ≠ H1
   - основной запрос отсутствует в title или H1
   - первый абзац не отвечает на запрос
   - canonical отсутствует или не совпадает с og:url/BreadcrumbList
4. Проверить важные проблемы:
   - слабый первый экран
   - нет внутренних ссылок на релевантные статьи
5. Исправить найденное (не переписывать статью целиком)
6. Задеплоить файл на FTP
7. Добавить в очередь переобхода Яндекса:
   curl -s -X POST \
     "https://api.webmaster.yandex.net/v4/user/$YANDEX_WEBMASTER_USER_ID/hosts/$YANDEX_WEBMASTER_HOST_ID/recrawl/queue" \
     -H "Authorization: OAuth $YANDEX_WEBMASTER_TOKEN" \
     -H "Content-Type: application/json" \
     -d "{\"url\": \"<URL страницы>\"}"
8. Статус в реестре: todo → done

## Ограничения
- Не переписывать статьи целиком
- Не добавлять неподтверждённые факты
- Деплоить после каждого изменения любого файла
- В конце: краткий итог по страницам и техническим файлам
