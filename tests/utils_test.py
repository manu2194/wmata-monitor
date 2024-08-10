import pytest
import json
from utils import convert_for_esp32_led_matrix_64_32


@pytest.mark.parametrize('input, output', [
    ({
        "line": {
            "RD": {
                "Shady Grove": [1, 2],
                "Glenmont": [1, 2],
            },
        },
        "timestamp": '2024-08-10T01:25:00.293639'
    },
        {
        "line": [
            {
                "name": "RD",
                "destinations": [
                    "Glen   1,2",
                    "Shad   1,2",
                ],
            }
        ],
        "timestamp": "01:25:00AM"
    }
    ),
    
    
    ({
        "line": {
            "RD": {
                "Glenmont": [1, 2],
                "Shady Grove": [1, 2, 3, 4],
            },
        },
        "timestamp": '2024-08-10T01:25:00.293639'
    },
        {
        "line": [
            {
                "name": "RD",
                "destinations": [
                    "Glen   1,2",
                    "Shad   1,2",
                ],
            }
        ],
        "timestamp": "01:25:00AM"
    }
    ),
    
    ({
        "line": {
            "RD": {
                "Glenmont": [1, 2],
            },
        },
        "timestamp": '2024-08-10T01:25:00.293639'
    },
        {
        "line": [
            {
                "name": "RD",
                "destinations": [
                    "Glen   1,2",
                ],
            }
        ],
        "timestamp": "01:25:00AM"
    }
    ),
    
    ({
        "line": {
            "RD": {
                "Glenmont": []
            },
        },
        "timestamp": '2024-08-10T01:25:00.293639'
    },
        {
        "line": [
            {
                "name": "RD",
                "destinations": [
                    "Glen",
                ],
            }
        ],
        "timestamp": "01:25:00AM"
    }
    ),
    
    ({
        "line": {
            "RD": {
                "Glenmont": [99,99]
            },
        },
        "timestamp": '2024-08-10T01:25:00.293639'
    },
        {
        "line": [
            {
                "name": "RD",
                "destinations": [
                    "Glen 99,99",
                ],
            }
        ],
        "timestamp": "01:25:00AM"
    }
    ),
    
    ({
        "line": {
            "RD": {
                "Glenmont": [99999,99999]
            },
        },
        "timestamp": '2024-08-10T01:25:00.293639'
    },
        {
        "line": [
            {
                "name": "RD",
                "destinations": [
                    "Glen 99999",
                ],
            }
        ],
        "timestamp": "01:25:00AM"
    }
    ),
])
def test_convert_for_esp32_led_matrix_64_32(input, output):
    actual = convert_for_esp32_led_matrix_64_32(input)
    assert json.dumps(actual) == json.dumps(output)
