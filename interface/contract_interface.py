from web3 import Web3
import json
import os
from web3.exceptions import ContractLogicError

# Подключение к локальной Hardhat-ноде
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
assert w3.is_connected(), "❌ Web3 не подключен"

# Адрес развернутого контракта
CONTRACT_ADDRESS = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"

# Абсолютный путь к ABI
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
abi_path = os.path.join(BASE_DIR, "artifacts", "contracts", "VectorStore.sol", "VectorStore.json")

print(f"📄 Загружаем ABI из: {abi_path}")

with open(abi_path, "r", encoding="utf-8") as f:
    contract_data = json.load(f)
    abi = contract_data["abi"]

# Создаем экземпляр контракта
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# Используем первый аккаунт по умолчанию
w3.eth.default_account = w3.eth.accounts[0]

# Утилиты
def get_vec_id(name: str) -> bytes:
    """Получить bytes32 id вектора по имени"""
    return w3.keccak(text=name)

def vector_exists(name: str) -> bool:
    """Проверить, существует ли вектор с таким id"""
    vec_id = get_vec_id(name)
    return contract.functions.vectorExists(vec_id).call()

def _sanitize_values(values) -> list[int]:
    """Привести значения к списку int для корректной сериализации"""
    sanitized = []
    for v in values:
        try:
            sanitized.append(int(v))
        except Exception as e:
            raise ValueError(f"Invalid vector value: {v} ({type(v)})") from e
    return sanitized

# Методы для хранения и обновления вектора с защитой от ошибок
def store_vector(name: str, values) -> dict:
    vec_id = get_vec_id(name)
    sanitized_values = _sanitize_values(values)
    try:
        tx = contract.functions.storeVector(vec_id, sanitized_values).transact()
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        return receipt
    except ContractLogicError as err:
        # Если вектор уже существует, переключаемся на обновление
        if "Vector already exists" in str(err):
            print("⚠️ Вектор уже существует, переключаемся на updateVector")
            return update_vector(name, values)
        else:
            raise

def update_vector(name: str, values) -> dict:
    vec_id = get_vec_id(name)
    sanitized_values = _sanitize_values(values)
    tx = contract.functions.updateVector(vec_id, sanitized_values).transact()
    receipt = w3.eth.wait_for_transaction_receipt(tx)
    return receipt

def get_vector(name: str) -> list[int]:
    vec_id = get_vec_id(name)
    return contract.functions.getVector(vec_id).call()

# Основная логика для теста
if __name__ == "__main__":
    vector_name = "my_vector"
    values = [1, 2, 3]

    try:
        # Можно проверить наличие, но store_vector умеет переключаться
        if vector_exists(vector_name):
            print("♻️ Вектор уже существует. Обновляем...")
            receipt = update_vector(vector_name, values)
        else:
            print("📦 Сохраняем новый вектор...")
            receipt = store_vector(vector_name, values)

        print("✅ Транзакция подтверждена:", receipt.transactionHash.hex())

        print("📡 Получаем вектор...")
        result = get_vector(vector_name)
        print("📌 Значения:", result)

    except Exception as e:
        print("❌ Ошибка:", str(e))