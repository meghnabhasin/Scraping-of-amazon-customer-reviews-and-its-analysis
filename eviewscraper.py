# -*- coding: utf-8 -*-
import scrapy


class EviewscraperSpider(scrapy.Spider):
    name = "eviewscraper"
    allowed_domains = ['http://www.amazon.in', 'www.amazon.in', 'amazon']
    count = 0
    start_urls = ['http://www.amazon.in/b?node=976389031']
    mydata = {}

    def parse(self, response):
        category_links = response.css(
            'div.acs-en-main-section-container > div.acs-en-middle-section  a::attr(href)').extract()
        self.base = self.allowed_domains[0]

        for booklink in category_links:
            if booklink is not None:
                next_page = response.urljoin(booklink)  # combines base url with the extracted url
                yield scrapy.Request(next_page, callback=self.parseBooks)
                # next_page = response.urljoin(category_links[0])
                # yield scrapy.Request(next_page, callback=self.parseBooks)

    def parseBooks(self, response):
        self.count += 1
        pagetitle = response.css('title::text').extract_first()
        # self.mydata={'category': pagetitle}
        book_items = response.css('#mainResults > ul>li')
        for item in book_items:
            # print(item.css('h2::text').extract_first())
            link = item.css('a::attr(href)').extract_first()

            if link is not None:
                yield scrapy.Request(link, callback=self.parseBookDetails)

    def parseBookDetails(self, response):
        title = response.css('title::text').extract_first()
        # self.mydata['bookname']=title
        review_link = response.css('#acrCustomerReviewLink::attr(href)').extract_first()
        if review_link is not None:
            yield scrapy.Request(self.base + review_link, callback=self.parseReviews)

    def parseReviews(self, response):
        # bookitle=response.css('div.product-title > h1 a::text').extract_first()
        reviews = response.css('#cm_cr-review_list > div.review')
        for review in reviews:
            yield {
                'BookName': response.css('div.product-title > h1 a::text').extract_first(),
                'author':response.css('div.product-by-line a::text').extract_first(),
                'reviewtitle': review.css('a::text').extract_first(),
                'name': review.css('a.author::text').extract_first(),
                'date': review.css('span.review-date::text').extract_first(),
                'review': review.css('span.review-text::text').extract_first()
            }
            nextlink=response.css('ul.a-pagination > li.a-last a::attr(href)').extract_first()
            if nextlink is not None:
                self.base = self.allowed_domains[0]
                next_page = response.urljoin(nextlink)
                yield scrapy.Request(next_page, callback=self.parseReviews)
