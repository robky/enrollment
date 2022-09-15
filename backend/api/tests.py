from datetime import datetime

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from core.models import TYPE_FILE, TYPE_NAME, FileSystem


class NodesTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()

        cls.imports_url = reverse("api:imports-list")
        cls.imports_url = reverse("api:delete")

        cls.item_folder = dict(
            id="test-100", url=None, type="FOLDER", parentId=None, size=None
        )
        cls.item_file = dict(
            id="test-101",
            url="test/file101",
            type="FILE",
            parentId=None,
            size=1,
        )
        cls.date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_item(self, node_type: int, **kwargs) -> dict:
        """У готового объекта меняет полученные значения. Возвращает готовый
        объект.
        node_type:  1 - папка, 2 - файл"""
        result = (
            self.item_folder.copy()
            if node_type == 1
            else self.item_file.copy()
        )
        for key, value in kwargs.items():
            result[key] = value
        return result

    def test_create_folder_and_file(self):
        """Проверка создания папки и файла"""
        tests = [self.item_folder, self.item_file]
        for number, test in enumerate(tests, 1):
            with self.subTest(type=test["type"], number=number):
                items = [test]
                import_data = dict(items=items, updateDate=self.date)
                nodes_count = FileSystem.objects.count()
                response = self.client.post(self.imports_url, import_data)

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(FileSystem.objects.count(), nodes_count + 1)
                new_node = FileSystem.objects.get(id=items[0]["id"])

                self.assertEqual(new_node.url, items[0]["url"])
                self.assertEqual(
                    new_node.date.strftime("%Y-%m-%dT%H:%M:%SZ"), self.date
                )
                self.assertEqual(new_node.parent_id, items[0]["parentId"])
                self.assertEqual(new_node.type, TYPE_NAME[items[0]["type"]])
                self.assertEqual(
                    new_node.size,
                    items[0]["size"] if new_node.type == TYPE_FILE else 0,
                )

    def test_dont_create_folder_or_file(self):
        """Проверка, что при неверных данных объект не создается"""
        tests = []

        # 1 Папка id не может быть null
        tests.append(self.get_item(node_type=1, id=None))
        # 2 Папка url всегда null
        tests.append(self.get_item(node_type=1, url="test"))
        # 3 Папка size всегда null
        tests.append(self.get_item(node_type=1, size=5))
        # 4 Файл id не может быть null
        tests.append(self.get_item(node_type=2, id=None))
        # 5 Файл url не может быть null
        tests.append(self.get_item(node_type=2, url=None))
        # 6 Файл url не может быть больше 255 символов
        tests.append(self.get_item(node_type=2, url="0" * 256))
        # 7 Файл url не может быть пустым
        tests.append(self.get_item(node_type=2, url=""))
        # 8 Файл size не может быть меньше нуля
        tests.append(self.get_item(node_type=2, size=-1))

        for number, test in enumerate(tests, 1):
            with self.subTest(type=test["type"], number=number):
                items = [test]
                import_data = dict(items=items, updateDate=self.date)
                nodes_count = FileSystem.objects.count()
                response = self.client.post(self.imports_url, import_data)

                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST
                )
                self.assertEqual(FileSystem.objects.count(), nodes_count)
                self.assertEqual(response.data["message"], "Validation Failed")

    def test_data_import(self):
        """Проверка, что если дата не ISO 8601, то объекты не создаются"""
        items = [self.item_folder, self.item_file]
        temp_data = datetime.now().strftime("%d-%m-%YT%H:%M:%SZ")
        import_data = dict(items=items, updateDate=temp_data)
        nodes_count = FileSystem.objects.count()
        response = self.client.post(self.imports_url, import_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FileSystem.objects.count(), nodes_count)
        self.assertEqual(response.data["message"], "Validation Failed")

    def test_unique_id_with_import(self):
        """Проверка, что если одинаковые id в одном запросе, то объектs не
        создаются"""
        items = [self.item_folder, self.item_folder]
        import_data = dict(items=items, updateDate=self.date)
        nodes_count = FileSystem.objects.count()
        response = self.client.post(self.imports_url, import_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FileSystem.objects.count(), nodes_count)
        self.assertEqual(response.data["message"], "Validation Failed")

    def test_parent_is_folder_import(self):
        """Проверка, что если родитель не папка, то объект не создается"""
        folder_parent = self.get_item(node_type=1, id="id00")
        file_parent = self.get_item(node_type=2, id="id01")
        items = [folder_parent, file_parent]
        import_data = dict(items=items, updateDate=self.date)
        nodes_count = FileSystem.objects.count()
        response = self.client.post(self.imports_url, import_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FileSystem.objects.count(), nodes_count + 2)

        folder_children = self.get_item(node_type=1, id="id00_1")
        file_children = self.get_item(
            node_type=1, id="id00_2", parentId="id01"
        )
        items = [folder_children, file_children]
        import_data = dict(items=items, updateDate=self.date)
        nodes_count = FileSystem.objects.count()
        response = self.client.post(self.imports_url, import_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FileSystem.objects.count(), nodes_count)
        self.assertEqual(response.data["message"], "Validation Failed")

    def test_change_size_and_date_parent(self):
        """Проверка, что меняется значение size и date у родительских папок при
        добавлении/изменинии файлов"""
        folder1 = self.get_item(node_type=1, id="node1")
        folder2 = self.get_item(node_type=1, id="node2", parentId="node1")
        folder3 = self.get_item(node_type=1, id="node3", parentId="node2")
        file1 = self.get_item(
            node_type=2, id="file1", parentId="node1", size=2
        )
        file2 = self.get_item(
            node_type=2, id="file2", parentId="node2", size=3
        )
        file3 = self.get_item(
            node_type=2, id="file3", parentId="node3", size=4
        )
        file4 = self.get_item(
            node_type=2, id="file4", parentId="node3", size=5
        )

        nodes_count = FileSystem.objects.count()
        tests = [[folder1], [folder2], [folder3], [file1, file2, file3, file4]]
        second = 1
        for test in tests:
            items = test
            updateDate = datetime(2022, 9, 1, 10, 20, second).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            import_data = dict(items=items, updateDate=updateDate)
            response = self.client.post(self.imports_url, import_data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            second += 5

        self.assertEqual(FileSystem.objects.count(), nodes_count + 7)
        node3 = FileSystem.objects.get(id=folder3["id"])
        self.assertEqual(node3.size, file3["size"] + file4["size"])
        self.assertEqual(node3.date.strftime("%Y-%m-%dT%H:%M:%SZ"), updateDate)
        node2 = FileSystem.objects.get(id=folder2["id"])
        self.assertEqual(node2.size, node3.size + file2["size"])
        self.assertEqual(node2.date.strftime("%Y-%m-%dT%H:%M:%SZ"), updateDate)
        node1 = FileSystem.objects.get(id=folder1["id"])
        self.assertEqual(node1.size, node2.size + file1["size"])
        self.assertEqual(node1.date.strftime("%Y-%m-%dT%H:%M:%SZ"), updateDate)

        # Меняем размер нижнего элемента
        file4["size"] = file4["size"] + 3
        items = [file4]
        date1 = datetime(2022, 9, 2, 11, 10).strftime("%Y-%m-%dT%H:%M:%SZ")
        import_data = dict(items=items, updateDate=date1)
        response = self.client.post(self.imports_url, import_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        node3 = FileSystem.objects.get(id=folder3["id"])
        self.assertEqual(node3.size, file3["size"] + file4["size"])
        self.assertEqual(node3.date.strftime("%Y-%m-%dT%H:%M:%SZ"), date1)
        node2 = FileSystem.objects.get(id=folder2["id"])
        self.assertEqual(node2.size, node3.size + file2["size"])
        self.assertEqual(node2.date.strftime("%Y-%m-%dT%H:%M:%SZ"), date1)
        node1 = FileSystem.objects.get(id=folder1["id"])
        self.assertEqual(node1.size, node2.size + file1["size"])
        self.assertEqual(node1.date.strftime("%Y-%m-%dT%H:%M:%SZ"), date1)

        # Перенесем нижний элемент на верх
        file4["parentId"] = folder1["id"]
        items = [file4]
        date2 = datetime(2022, 9, 3, 11, 10).strftime("%Y-%m-%dT%H:%M:%SZ")
        import_data = dict(items=items, updateDate=date2)
        response = self.client.post(self.imports_url, import_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        node3 = FileSystem.objects.get(id=folder3["id"])
        self.assertEqual(node3.size, file3["size"])
        self.assertEqual(node3.date.strftime("%Y-%m-%dT%H:%M:%SZ"), date2)
        node2 = FileSystem.objects.get(id=folder2["id"])
        self.assertEqual(node2.size, node3.size + file2["size"])
        self.assertEqual(node2.date.strftime("%Y-%m-%dT%H:%M:%SZ"), date2)
        node1 = FileSystem.objects.get(id=folder1["id"])
        self.assertEqual(
            node1.size, node2.size + file1["size"] + file4["size"]
        )
        self.assertEqual(node1.date.strftime("%Y-%m-%dT%H:%M:%SZ"), date2)
