"""
Contract data loader for the Contract Clause Analysis OpenEnv environment.

Provides a unified get_contracts() function to load data for any task.
"""

from data.contracts_easy import EASY_CONTRACTS
from data.contracts_medium import MEDIUM_CONTRACTS
from data.contracts_hard import HARD_CONTRACT_PAIRS


def get_contracts(task_id: str, contract_index: int | None = None):
    """
    Load contract data for a given task.

    Args:
        task_id: One of "clause_identification", "risk_flagging", "contract_comparison"
        contract_index: Optional index to get a specific contract. If None, returns all.

    Returns:
        A single contract dict or list of contract dicts.

    Raises:
        ValueError: If task_id is unknown or contract_index is out of range.
    """
    data_map = {
        "clause_identification": EASY_CONTRACTS,
        "risk_flagging": MEDIUM_CONTRACTS,
        "contract_comparison": HARD_CONTRACT_PAIRS,
    }

    if task_id not in data_map:
        raise ValueError(
            f"Unknown task_id: {task_id!r}. "
            f"Valid options: {list(data_map.keys())}"
        )

    contracts = data_map[task_id]

    if contract_index is not None:
        if contract_index < 0 or contract_index >= len(contracts):
            raise ValueError(
                f"contract_index {contract_index} out of range for task "
                f"{task_id!r} (has {len(contracts)} contracts)"
            )
        return contracts[contract_index]

    return contracts
