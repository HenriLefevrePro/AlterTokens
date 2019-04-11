import ldap3
import json
from pprint import pprint


server_uri = 'ldap://127.0.0.1:50389'
bind_dn = "cn=Directory Manager"
pw = "Admin001"
new_scope = "TestScope"

attrs = ["coreTokenObject","coreTokenString01"]

server = ldap3.Server(server_uri)
with ldap3.Connection(server, user=bind_dn, password=pw, auto_bind=True) as conn:
    obj_frCoreToken = ldap3.ObjectDef('frCoreToken', conn)
    r = ldap3.Reader(conn, obj_frCoreToken, "ou=famrecords,ou=openam-session,ou=tokens,dc=openam,dc=forgerock,dc=org")
    print(r)
    print(r.search())
    w = ldap3.Writer.from_cursor(r)
    print(w)
    for index, entry in enumerate(r):
        coreTokenObject = entry.entry_attributes_as_dict['coreTokenObject']
        if(coreTokenObject):
            coreTokenObject_json = json.loads(entry.entry_attributes_as_dict['coreTokenObject'][0])
            scopes_list = coreTokenObject_json['scope']
            if new_scope not in scopes_list:
                print ("testScope missing in index = " + str(index))
                print(type(coreTokenObject_json['scope']))
                coreTokenObject_json['scope'].append(new_scope)
                print("coreTokenObject_json['scope'] = "+ str(coreTokenObject_json['scope']))
                new_coreTokenObject = json.dumps(coreTokenObject_json) #Bug : Remove spaces from the JSON
                new_coreTokenString01 = ",".join(coreTokenObject_json['scope'])
                print("new_coreTokenObject = "+new_coreTokenObject)
                w[index].coreTokenObject = new_coreTokenObject
                w[index].coreTokenString01 = new_coreTokenString01
                print(w[index])
    w.commit()