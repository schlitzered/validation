__author__ = 'schlitzer'

import validation


user_validator = validation.Dict(ignore_unknown=False)
user_validator.required['_id'] = validation.StringUUID()
user_validator.required['name'] = validation.String()
user_validator.required['gender'] = validation.Choice(choices=['male', 'female'])
hobbies = validation.List()
hobbies.validator = validation.String()
user_validator.optional['hobbies'] = hobbies

john = {
    '_id': 'e7a5ff1c-ee5e-4ca9-a3d3-0106dd826dcd',
    'name': 'John',
    'gender': 'male',
    'hobbies': [
        'python',
        'blarg',
        'blub',
        1
    ]
}

paula = {
    '_id': 'e7a5ff1c-ee5e-4ca9-a3d3-0106dd826dcd',
    'name': 'Paula',
    'gender': 'female',
}

weirdo = {
    '_id': 'e7a5ff1c-ee5e-4ca9-a3d3-0106dd826dcd',
    'name': 'Weirdo',
    'gender': 'all of them',
    'hobbies': [
        'mitosis'
    ],
    'blarg': True
}

if __name__ == '__main__':
    for user in [john, paula, weirdo]:
        try:
            user_validator.validate(user)
            print("user is valid")
        except validation.ValidationError as err:
            print(err)
