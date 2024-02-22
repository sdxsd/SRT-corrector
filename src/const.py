# SUBTITLE-CORRECTOR IS LICENSED UNDER THE GNU GPLv3
# Copyright (C) 2023 Will Maguire

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>

# The definition of Free Software is as follows:
# 	- The freedom to run the program, for any purpose.
# 	- The freedom to study how the program works, and adapt it to your needs.
# 	- The freedom to redistribute copies so you can help your neighbor.
# 	- The freedom to improve the program, and release your improvements
#   - to the public, so that the whole community benefits.

# A program is free software if users have all of these freedoms.

# Models and their different prices per token.
API_prices = {
    "gpt-4-turbo-preview": {
        "input_price": 0.01 / 1000,
        "output_price": 0.03 / 1000
    },
    "gpt-4": {
        "input_price": 0.03 / 1000,
        "output_price": 0.06 / 1000
    },
    "gpt-4-32k": {
        "input_price": 0.06 / 1000,
        "output_price": 0.12 / 1000
    },
    "gpt-3.5-turbo-1106": {
        "input_price": 0.0010 / 1000,
        "output_price": 0.0020 / 1000
    },
    "gpt-3.5-turbo": {
        "input_price": 0.0010 / 1000,
        "output_price": 0.0020 / 1000
    }
}

# Tiers and their respective rate limits for GPT models.
Tiers = {
    0: {
        "gpt-3.5-turbo": {
            "RPM": 3,
            "TPM": 40000
        }
    },
    1: {
        "gpt-3.5-turbo": {
            "RPM": 3500,
            "TPM": 60000
        },
        "gpt-4": {
            "RPM": 500,
            "TPM": 10000
        },
        "gpt-4-turbo-preview": {
            "RPM": 500,
            "TPM": 150000
        }
    },
    2: {
        "gpt-3.5-turbo": {
            "RPM": 3500,
            "TPM": 80000
        },
        "gpt-4": {
            "RPM": 5000,
            "TPM": 40000
        },
        "gpt-4-turbo-preview": {
            "RPM": 5000,
            "TPM": 300000
        }
    },
    3: {
        "gpt-3.5-turbo": {
            "RPM": 3500,
            "TPM": 160000
        },
        "gpt-4": {
            "RPM": 5000,
            "TPM": 80000
        },
        "gpt-4-turbo-preview": {
            "RPM": 5000,
            "TPM": 300000
        }
    },
    4: {
        "gpt-3.5-turbo": {
            "RPM": 10000,
            "TPM": 1000000
        },
        "gpt-4": {
            "RPM": 10000,
            "TPM": 300000
        },
        "gpt-4-turbo-preview": {
            "RPM": 10000,
            "TPM": 450000
        }
    },
    5: {
        "gpt-3.5-turbo": {
            "RPM": 10000,
            "TPM": 2000000
        },
        "gpt-4": {
            "RPM": 10000,
            "TPM": 300000
        },
        "gpt-4-turbo-preview": {
            "RPM": 10000,
            "TPM": 600000
        }
    },
}
