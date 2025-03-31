# {{ application.submitter.first_name }} {{ application.submitter.last_name }}

## Leader

**Name**:
```
{{ application.submitter.first_name }} {{ application.submitter.last_name }}
```

**District**:
```
{{ application.submitter.profile.district }}
```

**Discord username**:
```
{{ application.submitter.profile.discord.extra_data.username }}
```

**{{ application.data.preferred_contact_method.label }}**:
```
{{ application.data.preferred_contact_method.value }}
```

## Nominating Organizer/Board Member
```
{{ application.data.nominator.value }}
```

## Desired role

**{{ application.data.primary_role.label }}**:
```
{{ application.data.primary_role.value }}
```

{% if application.data.primary_role_other.value == "other" %}
**{{ application.data.primary_other_role.label }}**:
```
{{ application.data.primary_otherrole.value }}
```
{% endif %}

**{{ application.data.regular_duties.label }}**
```
{{ application.data.regular_duties.value }}
```

**{{ application.data.teams.label }}**
```{% for team in application.data.teams.value %}
- {{ team }}{% endfor %}
```

## Past Involvement

**{{ application.data.involvement.label }}**
```
{{ application.data.involvement.value }}
```

**{{ application.data.past_experience.label }}**
```
{{ application.data.past_experience.value }}
```

**{{ application.data.current_contribution.label }}**
```
{{ application.data.current_contribution.value }}
```

{% if application.data.current_contribution_info.value %}
**{{ application.data.current_contribution_info.label }}**
```
{{ application.data.current_contribution_info.value }}
```
{% endif %}

## Availability

**{{ application.data.online_availability.label }}**
```
{{ application.data.online_availability.value }}
```

**{{ application.data.inperson_availability.label }}**
```
{{ application.data.inperson_availability.value }}
```

## Additional info

**{{ application.data.public_speaking.label }}**:
```
{{ application.data.public_speaking.value|default:"no response" }}
```

**{{ application.data.support_needed.label }}**:
```
{{ application.data.support_needed.value|default:"no response" }}
```

**{{ application.data.anything_else.label }}**:
```
{{ application.data.anything_else.value|default:"no response" }}
```

## Conduct

**Code of Conduct agreed**:
```
True
```

**{{ application.data.not_gonna_try_to_name_this.label }}**:
```
{{ application.data.not_gonna_try_to_name_this.value }}
```

{% if application.data.not_gonna_try_to_name_this_info.value %}
**{{ application.data.not_gonna_try_to_name_this_info.label }}**:
```
Response redacted by default. Only select PBA Admins can access this via bikeaction.org/admin/
```
{% endif %}
