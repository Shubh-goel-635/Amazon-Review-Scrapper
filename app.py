from bs4 import BeautifulSoup as bs
import requests
import lxml
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def home_page():
    return render_template('index.html')


@app.route('/scrap', methods=['POST', 'GET'])
def scrap():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/54.0.2840.71 Safari/537.36'}
    link = request.form['content'].strip()
    pages = request.form['page']
    pages = int(pages)
    if pages == 0:
        pages=50
    pages += 1
    review_count = 0
    page_count = 0
    review_list = list()
    try:
        product_page_req = requests.request('get', url=link, headers=headers)
        product_page = bs(product_page_req.content, 'lxml')
        name = product_page.find('span', {'id': 'productTitle'}).text.strip()
        all_reviews_url = "https://www.amazon.in" + \
                          product_page.find_all('a', attrs={'data-hook': 'see-all-reviews-link-foot'})[0][
                              'href'] + "&pageNumber="
        print(name)
        for i in range(1, pages):
            review_page_url = all_reviews_url + str(i)
            review_page_response = requests.request('get', url=review_page_url, headers=headers)
            review_page = bs(review_page_response.content, 'lxml')
            reviews = review_page.find_all('div', attrs={"data-hook": "review"})
            page_count += 1
            for review in reviews:
                try:
                    name = review.div.div.find_next('span', attrs={'class': 'a-profile-name'}).text
                except:
                    name = -1
                try:
                    rating = review.div.div.find_next('span', attrs={'class': 'a-icon-alt'}).text.split(' ')[0]
                except:
                    rating = -1
                try:
                    heading = review.div.div.find_next('a', attrs={"data-hook": "review-title"}).span.text
                except:
                    heading = -1
                try:
                    date = review.div.div.find_next('span', attrs={'data-hook': "review-date"}).text.replace(
                        'Reviewed in India on ', '', 1)
                except:
                    date = -1
                try:
                    varient = review.div.div.find_next('a', attrs={'data-hook': 'format-strip'}).text
                except:
                    varient = -1
                try:
                    comment = review.div.div.find_next('span', attrs={'data-hook': 'review-body'}).span.text.strip()
                except:
                    comment = -1
                try:
                    helpfull = \
                        review.div.div.find_next('span', attrs={'data-hook': 'helpful-vote-statement'}).text.replace(
                            ',',
                            '').split(
                            ' ')[0]
                except:
                    helpfull = -1

                data_dict = {'Name': name, 'Rating': rating, 'Heading': heading, 'Date': date, 'Varient': varient,
                             'Helpfull': helpfull, 'Comment': comment}
                print(data_dict)
                review_list.append(data_dict)
                review_count += 1
            print(review_count, page_count)
        print(review_list, review_count, page_count, sep='\n')
        return render_template('result.html', reviews=review_list)


    except:
        return "Something went wrong"


if __name__ == '__main__':
    app.run(debug=True)
