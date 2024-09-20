

"""
Напишіть Python-скрипт, який буде читати всі файли у вказаній користувачем
вихідній папці (source folder) і розподіляти їх по підпапках у директорії
призначення (output folder) на основі розширення файлів.
Скрипт повинен виконувати сортування асинхронно для більш ефективної
обробки великої кількості файлів.

Імпортуйте необхідні асинхронні бібліотеки.
#Створіть об'єкт ArgumentParser для обробки аргументів командного рядка.
Додайте необхідні аргументи для визначення вихідної та цільової папок.
Ініціалізуйте асинхронні шляхи для вихідної та цільової папок.
Напишіть асинхронну функцію read_folder, яка рекурсивно читає всі файли
у вихідній папці та її підпапках.
Напишіть асинхронну функцію copy_file, яка копіює кожен файл у відповідну
підпапку у цільовій папці на основі його розширення.
Налаштуйте логування помилок.
Запустіть асинхронну функцію read_folder у головному блоці.
"""

import argparse
import asyncio
from aiopath import AsyncPath
from aioshutil import copyfile
import logging


logger = logging.getLogger("asyncio")


def parse_args():
    parser = argparse.ArgumentParser(description="Source folder path")
    parser.add_argument('source_folder', type=str, help='Source folder path')
    parser.add_argument('output_folder', type=str,
                        help='Destination folder path')
    args = parser.parse_args()
    return (AsyncPath(args.source_folder), AsyncPath(args.output_folder))


async def read_folder(source_folder, output_folder):
    try:
        if not await source_folder.exists() or \
            not await source_folder.is_dir():
            logger.error(f"""Source folder '{source_folder}'
                         does not exist or not a directory.""")
            return

        async for item in source_folder.glob('*'):
            assert isinstance(item, AsyncPath)
            if await item.is_file():
                await copy_file(item, output_folder)
            elif await item.is_dir():
                await read_folder(item, output_folder)
    except Exception as e:
        logger.error(f"Error reading folder: {e}")


async def copy_file(file_path, output_folder):
    try:
        extention = file_path.suffix.lower()
        target_folder: AsyncPath = output_folder / extention.strip('.')

        await target_folder.mkdir(exist_ok=True, parents=True)

        target_file = target_folder / file_path.name
        await copyfile(file_path, target_file)
        logger.info(f"Copied {file_path} to {target_file}")
    except Exception as e:
        logger.error(f"Error copying file {file_path}: {e}")


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    source_folder, output_folder = parse_args()
    asyncio.run(read_folder(source_folder, output_folder))
