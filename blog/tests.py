from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post
from django.contrib.auth.models import User


# Create your tests here.


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')

    def navbar_test(self,soup):
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
        # 포스트 목록 페이지 가져오기
        response = self.client.get('/blog/')
        # 정상적으로 페이지 로드된다
        self.assertEqual(response.status_code, 200)
        # 페이지 타이틀은 'Blog' 이다
        soup = BeautifulSoup(response.content, "html.parser")
        # 내비게이션 바가 있다
        self.navbar_test(soup)
        #
        # 메인영역에 게시물이 하나도 없다면
        self.assertEqual(Post.objects.count(), 0)

        # 아직 게시물이 없습니다라는 문구가 보인다
        main_area = soup.find('div', id='main-area')
        self.assertIn("아직 게시물이 없습니다.", main_area.text)

        # 게시물이 2개 있다면
        post_001 = Post.objects.create(
            title='첫번쨰 포스트',
            content="hello world we are the world",
            author=self.user_trump
        )
        post_002 = Post.objects.create(
            title='두번쨰 포스트',
            content="1등이 전부는 아니잖아요?",
            author=self.user_obama
        )
        self.assertEqual(Post.objects.count(), 2)
        # 포스트 목록 페이지를 새로고침했을때
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, "html.parser")
        self.assertEqual(response.status_code, 200)
        # 메인 영역에 포스트2개의 타이틀이 존재한다
        main_area = soup.find('div', id='main-area')
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        # 아직 게시물이 없습니다 라는 문구는 더이상 보이지 않는다.
        self.assertNotIn('아직 게시물이 없습니다.', main_area.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

    def test_post_detail(self):
        post_001 = Post.objects.create(
            title="첫번째 포스트입니다",
            content='hello world we are the world',
            author=self.user_trump
        )

        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')

        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")

        self.navbar_test(soup)
        self.assertIn(post_001.title, soup.title.text)

        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(post_001.content, post_area.text)



