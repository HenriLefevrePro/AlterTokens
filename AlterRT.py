import ldap3 # https://ldap3.readthedocs.io/#
import json

# Server connection data
server_uri = 'ldap://127.0.0.1:50389'
# Service account credentials
bind_dn = "cn=Directory Manager"
pw = "Admin001"
# Scope to be added
new_scope = "TestScope"
# Attributes to be gathered 
attrs = ["coreTokenObject", "coreTokenString01"]
# organisationalUnit where the tokens can be found
tokenOU = "ou=famrecords,ou=openam-session,ou=tokens,dc=openam,dc=forgerock,dc=org"

# Creating a Server object
server = ldap3.Server(server_uri)
# Creating a Connection context to connect to the Server with service account credentials
with ldap3.Connection(server, user=bind_dn, password=pw, auto_bind=True) as conn:
    # Creating an ObjectDef object to represent frCoreToken objectClass
    obj_frCoreToken = ldap3.ObjectDef('frCoreToken', conn)
    # Creating a Reader object to read LDAP objects in the token organisationalUnit
    r = ldap3.Reader(conn, obj_frCoreToken, tokenOU)
    print(r)
    print(r.search())
    # Creating a Writer object fron the Reader to be able to edit LDAP entries
    w = ldap3.Writer.from_cursor(r)
    print(w)
    for index, entry in enumerate(r):
        # Gathering the coreTokenObject field from the current entry
        coreTokenObject = entry.entry_attributes_as_dict['coreTokenObject']
        # Checking that the coreTokenObject field (list) is not empty
        if(coreTokenObject):
            # Reading the coreTokenObject field as a JSON (string to JSON)
            coreTokenObject_json = json.loads(entry.entry_attributes_as_dict['coreTokenObject'][0])
            # Reading the scopes field of the coreTokenObject
            scopes_list = coreTokenObject_json['scope']
            # Checking whether the new scope is already in the coreTokenObject
            if new_scope not in scopes_list:
                print ("testScope missing in index = " + str(index))
                print(type(coreTokenObject_json['scope']))
                # Adding the new scope to the JSON object
                coreTokenObject_json['scope'].append(new_scope)
                print("coreTokenObject_json['scope'] = "+ str(coreTokenObject_json['scope']))
                # Creting a new string to update the coreTokenObject
                new_coreTokenObject = json.dumps(coreTokenObject_json) #Bug : Remove spaces from the JSON
                # Creating a new string to update the coreTokenString01 from the coreTokenObject scopes
                new_coreTokenString01 = ",".join(coreTokenObject_json['scope'])
                print("new_coreTokenObject = "+new_coreTokenObject)
                # Adding coreTokenObject update to the Writer
                w[index].coreTokenObject = new_coreTokenObject
                # Adding coreTokenString01 update to the Writer
                w[index].coreTokenString01 = new_coreTokenString01
                print(w[index])
    # Commiting changes to the CTS LDAP
    w.commit()