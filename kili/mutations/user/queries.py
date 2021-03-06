from .fragments import AUTH_PAYLOAD_FRAGMENT, USER_FRAGMENT

GQL_SIGN_IN = f'''
mutation($email: String!, $password: String!) {{
  data: signIn(email: $email password: $password) {{
    {AUTH_PAYLOAD_FRAGMENT}
  }}
}}
'''

GQL_CREATE_USER = f'''
mutation(
    $name: String!
    $email: String!
    $password: String!
    $phone: String
    $organizationRole: OrganizationRole!
) {{
  data: createUser(name: $name
      email: $email
      password: $password
      phone: $phone
      organizationRole: $organizationRole) {{
    {USER_FRAGMENT}
  }}
}}
'''

GQL_CREATE_USER_FROM_EMAIL_IF_NOT_EXISTS = f'''
mutation(
    $name: String!
    $email: String!
    $organizationRole: OrganizationRole!
    $projectID: String!
) {{
  data: createUserFromEmailIfNotExists(name: $name
      email: $email
      organizationRole: $sorganizationRole
      projectID: $projectID) {{
    {USER_FRAGMENT}
  }}
}}
'''

GQL_UPDATE_USER = f'''
mutation(
    $userID: ID!
    $name: String!
    $email: String!
    $phone: String
    $organizationRole: OrganizationRole
) {{
  data: updateUser(userID: $userID
      name: $name
      email: $email
      phone: $phone
      organizationRole: $organizationRole) {{
    {USER_FRAGMENT}
  }}
}}
'''

GQL_UPDATE_PASSWORD = f'''
mutation(
    $email: String!
    $oldPassword: String!
    $newPassword1: String!
    $newPassword2: String!
) {{
  data: updatePassword(email: $email
      oldPassword: $oldPassword
      newPassword1: $newPassword1
      newPassword2: $newPassword2) {{
    {USER_FRAGMENT}
  }}
}}
'''

GQL_RESET_PASSWORD = f'''
mutation($email: String!) {{
  data: resetPassword(email: $email) {{
    {USER_FRAGMENT}
  }}
}}
'''

GQL_UPDATE_PROPERTIES_IN_USER = f'''
mutation(
    $email: String!
    $name: String
    $organizationId: String
    $organizationRole: String
    $activated: Boolean
) {{
  data: updatePropertiesInUser(
    where: {{email: $email}}
    data: {{
      name: $name
      organizationId: $organizationId
      organizationRole: $organizationRole
      activated: $activated
    }}
  ) {{
    {USER_FRAGMENT}
  }}
}}
'''
