# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2021 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import inspect
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Union, Iterable

if TYPE_CHECKING:
    from openai.openai_object import OpenAIObject

Inputs = Dict[str, Any]
Outputs = Dict[str, Any]
Metadata = Dict[str, Any]


def create_arguments_supported(kwargs: Dict[str, Any]) -> bool:
    if "messages" not in kwargs:
        return False

    return True


def parse_create_arguments(kwargs: Dict[str, Any]) -> Tuple[Inputs, Metadata]:
    kwargs_copy = kwargs.copy()
    inputs = {}

    inputs["messages"] = kwargs_copy.pop("messages")
    if "function_call" in kwargs_copy:
        inputs["function_call"] = kwargs_copy.pop("function_call")

    metadata = {"created_from": "openai", "type": "openai_chat", **kwargs_copy}

    return inputs, metadata


def parse_create_result(result: Union["OpenAIObject", Iterable["OpenAIObject"]]) -> Tuple[Outputs, Metadata]:
    if inspect.isgenerator(result):
        choices = "Generation is not logged when using stream mode"
        usage = "Usage is not logged when using stream mode"
    else:
        choices: List[Dict[str, str]] = [
            choice.message.to_dict() for choice in result.choices
        ]
        usage = result.usage.to_dict()

    outputs = {"choices": choices}
    metadata = {"usage": usage}

    return outputs, metadata
