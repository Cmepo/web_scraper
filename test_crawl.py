import unittest
from crawl import *

class TestCrawl(unittest.TestCase):

    def test_normalize_url(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual,expected)

    def test_normalize_url2(self):
        expected = "www.boot.dev/blog/path"
        test_cases = [
            ("https://www.boot.dev/blog/path/"),
            ("https://www.boot.dev/blog/path"),
            ("http://www.boot.dev/blog/path/"),
            ("http://www.boot.dev/blog/path"),
        ]
        for input_url in test_cases:
            with self.subTest(input_url=input_url):
                actual=normalize_url(input_url)
                self.assertEqual(actual,expected)

    def test_get_heading_from_html(self):
        test_cases = [
            ("<html><body><h1>Test Title</h1></body></html>",
                "Test Title"),
            ("<html><body><h1>Hello <span>World</span></h1></body></html>",
                "Hello World"),
            ("<html><body><p>No heading here</p></body></html>",
                ""),
        ]
        for input_body, expected in test_cases:
            with self.subTest(input_body=input_body):
                actual = get_heading_from_html(input_body)
                self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html(self):
        test_cases = [
            ("""
                <html><body>
                    <p>Outside paragraph.</p>
                    <main>
                        <p>Main paragraph.</p>
                    </main>
                </body></html>
                """,
                "Main paragraph."
            ),
            ("""
                <html><body>
                    <p>First paragraph.</p>
                    <p>Second paragraph.</p>
                </body></html>
                """,
                "First paragraph."
            ),
            ("""
                <html><body>
                    <main>
                        <p>First main paragraph.</p>
                        <p>Second main paragraph.</p>
                    </main>
                </body></html>
                """,
                "First main paragraph."
            ),
        ]
        for input_body, expected in test_cases:
            with self.subTest(input_body=input_body):
                actual = get_first_paragraph_from_html(input_body)
                self.assertEqual(actual, expected)

    def test_get_urls_from_html(self):
        base_url = "https://crawler-test.com"
        test_cases = [
            ('<a href="https://boot.dev">Boot</a>', ["https://boot.dev"]),
            ('<a href="/blog">Blog</a>', [f"{base_url}/blog"]),
            ('<a href="about">About</a>', [f"{base_url}/about"]),
            ('<a href="/a">A</a><a href="/b">B</a>', [f"{base_url}/a", f"{base_url}/b"]),
            ('<a href="https://other.com">Other</a>', ["https://other.com"]),
            ('<p>No links here</p>', []),
        ]

        for html, expected in test_cases:
            with self.subTest(html=html):
                self.assertEqual(get_urls_from_html(html, base_url), expected)

    def test_get_images_from_html(self):
        base_url = "https://crawler-test.com"
        test_cases = [
            ('<img src="https://boot.dev/logo.png">', ["https://boot.dev/logo.png"]),
            ('<img src="/logo.png">', [f"{base_url}/logo.png"]),
            ('<img src="images/logo.png">', [f"{base_url}/images/logo.png"]),
            ('<img src="/a.png"><img src="/b.jpg">', [f"{base_url}/a.png", f"{base_url}/b.jpg"]),
            ('<img src="https://other.com/pic.jpg">', ["https://other.com/pic.jpg"]),
            ('<p>No images here</p>', []),
        ]

        for html, expected in test_cases:
            with self.subTest(html=html):
                self.assertEqual(get_images_from_html(html, base_url), expected)
    
    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_relative(self):
        url = "https://example.com/blog/page"
        html = '<h1>Blog</h1><p>Hello!</p><a href="../about">About</a>'
        expected = {
            "url": url,
            "heading": "Blog",
            "first_paragraph": "Hello!",
            "outgoing_links": ["https://example.com/about"],
            "image_urls": [],
        }
        self.assertEqual(extract_page_data(html, url), expected)


    def test_extract_page_data_multiple(self):
        url = "https://example.com"
        html = '<h1>Title</h1><p>First</p><p>Second</p><a href="/a">A</a><a href="/b">B</a><img src="/1.png"><img src="/2.png">'
        expected = {
            "url": url,
            "heading": "Title",
            "first_paragraph": "First",
            "outgoing_links": [f"{url}/a", f"{url}/b"],
            "image_urls": [f"{url}/1.png", f"{url}/2.png"],
        }
        self.assertEqual(extract_page_data(html, url), expected)


    def test_extract_page_data_no_heading(self):
        url = "https://example.com"
        html = '<html><body><p>Just a paragraph.</p></body></html>'
        expected = {
            "url": url,
            "heading": "",
            "first_paragraph": "Just a paragraph.",
            "outgoing_links": [],
            "image_urls": [],
        }
        self.assertEqual(extract_page_data(html, url), expected)


    def test_extract_page_data_main_priority(self):
        url = "https://example.com"
        html = '<h1>Title</h1><p>Outside</p><main><p>Inside</p></main>'
        expected = {
            "url": url,
            "heading": "Title",
            "first_paragraph": "Inside",
            "outgoing_links": [],
            "image_urls": [],
        }
        self.assertEqual(extract_page_data(html, url), expected)


    def test_extract_page_data_empty(self):
        url = "https://example.com"
        html = "<html><body></body></html>"
        expected = {
            "url": url,
            "heading": "",
            "first_paragraph": "",
            "outgoing_links": [],
            "image_urls": [],
        }
        self.assertEqual(extract_page_data(html, url), expected)

    def test_normalize_url_root(self):
        self.assertEqual(normalize_url("https://example.com/"), "example.com")

    def test_normalize_url_nested(self):
        self.assertEqual(normalize_url("https://example.com/a/b/"), "example.com/a/b")

    def test_get_heading_from_html_missing(self):
        self.assertEqual(get_heading_from_html("<p>No heading</p>"), "")

    def test_get_first_paragraph_from_html_missing(self):
        self.assertEqual(get_first_paragraph_from_html("<h1>Title</h1>"), "")

if __name__ == "__main__":
    unittest.main()