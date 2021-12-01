
from google.scraper import Google

google_scraper = Google()

meta_history = google_scraper.get_metadata()

players_to_scrape = set(meta_history[meta_history.is_learned == 1]['Player'])
print('Player already scraped : \n')
print(players_to_scrape)


new_player = list(meta_history[meta_history.is_learned == 0]['Player'])[0]
print('New player to scrape : \n')
print(new_player)

print('\n\n')
players_to_scrape.update([new_player])


for player in players_to_scrape : 
    google_scraper.set_player(player)
    google_scraper.scroll_all_pages()
    google_scraper.get_images_urls()
    google_scraper.download_images_and_upload_bucket()


google_scraper.close_driver()