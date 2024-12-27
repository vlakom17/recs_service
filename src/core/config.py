import yaml
import argparse

class Config:
    log_level: str = "info"
    dbconnection: str = None
    port: int = 8001

    def load(self, path: str):
        """Загружает конфигурацию из YAML-файла."""
        try:
            with open(path, 'r') as file:
                config_data = yaml.safe_load(file)

            # Обновляем атрибуты класса из файла конфигурации
            if config_data:
                for key, value in config_data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)

        except FileNotFoundError:
            raise ValueError(f"Файл конфигурации не найден: {path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Ошибка при разборе YAML: {e}")

    def __repr__(self):
        return f"Config(log_level={self.log_level}, dbconnection={self.dbconnection}, port={self.port})"


def parse_args():
    """Позваляет использовать аргумент --config для указания пути к конфигу."""
    parser = argparse.ArgumentParser(description="Parse configuration file path.")
    parser.add_argument(
        "--config",
        type=str,
        default="./configs/dev.yml",
        help="Path to the configuration file"
    )
    return parser.parse_args()

"""
Установленный конфиг приложения. Берётся из файла указанного по ключу --config или по умолчанию "./configs/dev.yml".
"""
cfg = Config()
cfg.load(parse_args().config)
