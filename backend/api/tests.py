from datetime import datetime

from rest_framework import status
from rest_framework.reverse import reverse

from rest_framework.test import APITestCase, APIClient

from core.models import FileSystem, TYPE_NAME, TYPE_FILE


class NodesTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()

        cls.imports_url = reverse('api:imports-list')

        cls.item_folder = dict(
            id='test-100',
            url=None,
            type='FOLDER',
            parentId=None,
            size=None
        )
        cls.item_file = dict(
            id='test-101',
            url='test/file101',
            type='FILE',
            parentId=None,
            size=1
        )
        cls.date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    def test_create_folder_and_file(self):
        """ Проверка создания папки и файла """
        tests = [self.item_folder, self.item_file]
        for number, test in enumerate(tests, 1):
            with self.subTest(type=test['type'], number=number):
                items = [test]
                node_folder = dict(items=items, updateDate=self.date)
                node_count = FileSystem.objects.count()
                response = self.client.post(self.imports_url, node_folder)

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(FileSystem.objects.count(), node_count + 1)
                new_node = FileSystem.objects.get(id=items[0]['id'])

                self.assertEqual(new_node.url, items[0]['url'])
                self.assertEqual(
                    new_node.date.strftime("%Y-%m-%dT%H:%M:%SZ"), self.date)
                self.assertEqual(new_node.parent_id, items[0]['parentId'])
                self.assertEqual(new_node.type, TYPE_NAME[items[0]['type']])
                self.assertEqual(
                    new_node.size,
                    items[0]['size'] if new_node.type == TYPE_FILE else 0)

    def test_dont_create_folder_or_file(self):
        """ Проверка, что при неверных данных объект не создается """
        tests = []

        # 1 Папка id не может быть null
        temp = self.item_folder.copy()
        temp['id'] = None
        tests.append(temp)
        # 2 Папка url всегда null
        temp = self.item_folder.copy()
        temp['url'] = 'test'
        tests.append(temp)
        # 3 Папка size всегда null
        temp = self.item_folder.copy()
        temp['size'] = 5
        tests.append(temp)
        # 4 Файл id не может быть null
        temp = self.item_file.copy()
        temp['id'] = None
        tests.append(temp)
        # 5 Файл url не может быть null
        temp = self.item_file.copy()
        temp['url'] = None
        tests.append(temp)
        # 6 Файл url не может быть больше 255 символов
        temp = self.item_file.copy()
        temp['url'] = "0" * 256
        tests.append(temp)
        # 7 Файл url не может быть пустым
        temp = self.item_file.copy()
        temp['url'] = ""
        tests.append(temp)
        # 8 Файл size не может быть меньше нуля
        temp = self.item_file.copy()
        temp['size'] = -1
        tests.append(temp)

        for number, test in enumerate(tests, 1):
            with self.subTest(type=test['type'], number=number):
                items = [test]
                node_folder = dict(items=items, updateDate=self.date)
                node_count = FileSystem.objects.count()
                response = self.client.post(self.imports_url, node_folder)

                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(FileSystem.objects.count(), node_count)
                self.assertEqual(response.data['message'], 'Validation Failed')

    def test_data_import(self):
        """ Проверка, что если дата не ISO 8601, то объект не создается """
        items = [self.item_folder, self.item_file]
        temp_data = datetime.now().strftime("%d-%m-%YT%H:%M:%SZ")
        node_folder = dict(items=items, updateDate=temp_data)
        node_count = FileSystem.objects.count()
        response = self.client.post(self.imports_url, node_folder)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FileSystem.objects.count(), node_count)
        self.assertEqual(response.data['message'], 'Validation Failed')