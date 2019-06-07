## TODO
Перевести проект в нормальную структуру по примеру: https://github.com/requests/requests

https://github.com/pypa/twine



## Утилита интерпретации данных

Читает исходные данные в объект-словарь

### Features
* Может работать как с файлами, так и с потоком
* Поддержка winpcap (https://github.com/orweis/winpcapy)
* Парсит в объект
* Парсит в объект + мета/компактная мета

## TODO
* Разные названия длины поля привести к одному
* Автоматическое определение формата
* Для полей типа BytesField не сериализовать данные
* Несколько регионов у одного поля (dos_header)
* Переделать массив с размером "до конца", убрать исключения
* meta для битов, перечислений
* human readable
* Выходной бинарный формат (msgpack например)
    - сериализация даты/времени и кастомных типов
    - передача типа данных
* БД на вход
* Импорт форматов
* Поддержка форматов:
    * HTTP
    * WIN PE
    * PNG, BMP, XCF, JPG, GIF
    * ZIP, TAR, GZ, BZ, GZIP
    * ELF
    * msgpack
    * pickle
    * XML, JSON, YAML и прочих

## TOOLS
* Сниффер
    * GUI
    * Группировка TCP и UDP в stream
* MitM tool
    * Сохранение журнала в БД
* Web-форма
* RPC
* npyscreen


##### Аналоги:
-	OpenDDL (http://openddl.org/)
-	DFDL (https://en.wikipedia.org/wiki/Data_Format_Description_Language)

##### WireShark:
-	https://stackoverflow.com/questions/4904991/how-can-i-add-a-custom-protocol-analyzer-to-wireshark
-	https://github.com/diacritic/wssdl
-	http://wsgd.free.fr/
-	https://wiki.wireshark.org/Asn2wrs
-	https://csjark.readthedocs.io/en/latest/
	