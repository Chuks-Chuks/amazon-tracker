from pages.amazon import SearchAmazon
import pytest

@pytest.mark.amazon
@pytest.mark.parametrize('product', ['ps5', 'violin', 'headphones', 'wireless mouse', 'carpet'])
@pytest.mark.usefixtures('driver', 'logger')
def test_searchamazon(driver, logger, product):
    logger.info(f'Starting the search for {product}')
    search = SearchAmazon(driver=driver)
    search.load()
    logger.info(f'Filling the search box with {product}')
    search.fill_search_box(product=product)
    logger.info(f'Sending details to database')
    search.send_to_db()
    driver.save_screenshot(f'../screenshots/{product}_passed.png')

    assert f'{product}' in driver.title.lower()