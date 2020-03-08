from bs4 import BeautifulSoup


def get_listed_items(html):
    """Retrieve items listed inside a HTML Table object. This
    function is used to extract Areas and Input names from a raw
    HTML page.

    Args:
        html: the HTML body containing the access token
    Returns:
        A list with the associated names (if any)
    """
    tree = BeautifulSoup(html, "html.parser")
    rows = tree.select("tbody > tr")
    return [x.getText().split("\n")[1] for x in rows]
