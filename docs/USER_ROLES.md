Anyone with an ORCID can login without being added to the special roles file ([ORCID.json](../orcid.json)). Supervisors must manually be added to ORCID.json.

```
If logged in with ORCID auth:
    if we add you to the list of supervisor users:
        your session role = supervisor
    Else: 
        your session role = general

If session role == supervisor, special privileges include:
	Can add custom topics
	Apps you add are automatically verified
	Can delete applications
	Can unlink datasets
	Can verify applications
    Can verify datasets
    Can see unverified applications
    Can undo changes
    Can import via CSV
```

See [before_routes.py](../routes/before_routes.py) for routes that are protected by role.