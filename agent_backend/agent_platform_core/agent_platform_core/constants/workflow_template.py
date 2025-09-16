"""
@Date    ：2024/8/20 1:34 
@Version: 1.0
@Description:

"""
import time

default_init_workflow_data = {
    "nodes": [
        {
            "id": str(int(time.time() * 1000)),
            "type": "custom",
            "data": {
                "type": "start",
                "title": "开始",
                "desc": "",
                "variables": [],
                "selected": False
            },
            "position": {
                "x": 30,
                "y": 226
            },
            "targetPosition": "left",
            "sourcePosition": "right",
            "positionAbsolute": {
                "x": 30,
                "y": 226
            },
            "width": 243,
            "height": 52,
            "selected": False
        }
    ],
    "edges": [],
    "viewport": {
        "x": 0,
        "y": 0,
        "zoom": 0.7
    }
}

default_init_feature = \
    {
        "opening_statement": "",
        "suggested_questions": [],
        "suggested_questions_after_answer": {
            "enabled": False
        },
        "text_to_speech": {
            "enabled": False,
            "voice": "",
            "language": ""
        },
        "speech_to_text": {
            "enabled": False
        },
        "retriever_resource": {
            "enabled": True
        },
        "sensitive_word_avoidance": {
            "enabled": False
        },
        "file_upload": {
            "image": {
                "enabled": False,
                "number_limits": 3,
                "transfer_methods": [
                    "local_file",
                    "remote_url"
                ]
            }
        }
    }
