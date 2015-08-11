Usage Example
*************

Sample Validator Usage
----------------------
.. code:: python

    import validation

    # Build the validation model

    user_validator = validation.Dict()
    user_validator.required['_id'] = validation.StringUUID()
    user_validator.required['name'] = validation.String()
    user_validator.required['gender'] = validation.Choice(choices=['male', 'female'])
    hobbies = validation.List()
    hobbies.validator = validation.String()
    user_validator.optional['hobbies'] = validation.List()

    # two valid user objects

    john = {
        '_id': 'e7a5ff1c-ee5e-4ca9-a3d3-0106dd826dcd',
        'name': 'John',
        'gender': 'male',
        'hobbies:': [
            'python',
            'blarg',
            'blub'
        ]
    }

    paula = {
        '_id': 'e7a5ff1c-ee5e-4ca9-a3d3-0106dd826dcd',
        'name': 'Paula',
        'gender': 'female',
    }

    # an not valid one

    weirdo = {
        '_id': 'e7a5ff1c-ee5e-4ca9-a3d3-0106dd826dcd',
        'name': 'Weirdo',
        'gender': 'all of them',
        'hobbies:': [
            'mitosis'
        ]
    }

if __name__ == '__main__':
    for user in [john, paula, weirdo]:
        try:
            # None is returned of the user is valid
            user_validator.validate(john)
        except validation.ValidationError as err:
            # a exception is raised, if the object is invalid
            # the exception message contains the first failed element
            print(err)

