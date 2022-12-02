from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category, Tag
from django.contrib.auth.models import User


# Create your tests here.


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')
        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')
        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')

        self.post_001 = Post.objects.create(
            title='첫번쨰 포스트',
            content="hello world we are the world",
            author=self.user_trump,
            category=self.category_programming
        )
        self.post_001.tags.add(self.tag_hello)
        self.post_002 = Post.objects.create(
            title='두번쨰 포스트',
            content="1등이 전부는 아니잖아요?",
            author=self.user_obama,
            category=self.category_music
        )
        self.post_003 = Post.objects.create(
            title='세번쨰 포스트',
            content='카테고리가 없을수도 있죠',
            author=self.user_obama
        )
        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_python)

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)
        self.assertIn(self.category_programming.name, soup.find('h1', id='category-header').text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f"{self.category_programming.name}({self.category_programming.post_set.count()})",
                      categories_card.text)
        self.assertIn(f"{self.category_music.name}({self.category_music.post_set.count()})",
                      categories_card.text)

        self.assertIn(f'미분류(1)', categories_card.text)

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn("About ME", navbar.text)

        logo_btn = navbar.find('a', text='MR Class')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About ME')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def test_post_list(self):
        # 포스트가 있는경우
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")
        self.navbar_test(soup)
        self.category_card_test(soup)
        main_area = soup.find('div', id='main-area')
        self.assertNotIn("아직 게시물이 없습니다.", main_area.text)
        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.post_001.author.username.upper(), post_001_card.text)

        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertIn(self.post_002.author.username.upper(), post_002_card.text)

        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)
        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.post_003.author.username.upper(), post_003_card.text)

        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

        # 포스트가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, "html.parser")
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다.', main_area.text)

        # # 포스트 목록 페이지 가져오기
        # response = self.client.get('/blog/')
        # # 정상적으로 페이지 로드된다
        # self.assertEqual(response.status_code, 200)
        # # 페이지 타이틀은 'Blog' 이다
        # soup = BeautifulSoup(response.content, "html.parser")
        # # 내비게이션 바가 있다
        # self.navbar_test(soup)
        # #
        # # 메인영역에 게시물이 하나도 없다면
        # self.assertEqual(Post.objects.count(), 0)
        #
        # # 아직 게시물이 없습니다라는 문구가 보인다
        # main_area = soup.find('div', id='main-area')
        # self.assertIn("아직 게시물이 없습니다.", main_area.text)
        #
        # # 게시물이 2개 있다면
        # post_001 = Post.objects.create(
        #     title='첫번쨰 포스트',
        #     content="hello world we are the world",
        #     author=self.user_trump
        # )
        # post_002 = Post.objects.create(
        #     title='두번쨰 포스트',
        #     content="1등이 전부는 아니잖아요?",
        #     author=self.user_obama
        # )
        # self.assertEqual(Post.objects.count(), 2)
        # # 포스트 목록 페이지를 새로고침했을때
        # response = self.client.get('/blog/')
        # soup = BeautifulSoup(response.content, "html.parser")
        # self.assertEqual(response.status_code, 200)
        # # 메인 영역에 포스트2개의 타이틀이 존재한다
        # main_area = soup.find('div', id='main-area')
        # self.assertIn(post_001.title, main_area.text)
        # self.assertIn(post_002.title, main_area.text)
        # # 아직 게시물이 없습니다 라는 문구는 더이상 보이지 않는다.
        # self.assertNotIn('아직 게시물이 없습니다.', main_area.text)
        #
        # self.assertIn(self.user_trump.username.upper(), main_area.text)
        # self.assertIn(self.user_obama.username.upper(), main_area.text)

    def test_post_detail(self):
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")

        self.navbar_test(soup)
        self.category_card_test(soup)
        self.assertIn(self.post_001.title, soup.title.text)

        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)
        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)
