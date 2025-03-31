# {{ application.submitter.first_name|safe }} {{ application.submitter.last_name|safe }}

## Leader

**Name**:
```
{{ application.submitter.first_name|safe }} {{ application.submitter.last_name|safe }}
```

**District**:
```
{{ application.submitter.profile.district|safe }}
```

**Discord username**:
```
{{ application.submitter.profile.discord.extra_data.username|safe }}
```

**{{ application.data.preferred_contact_method.label|safe }}**:
```
{{ application.data.preferred_contact_method.value|safe }}
```

## Nominating Organizer/Board Member
```
{{ application.data.nominator.value|safe }}
```

## Desired role

**{{ application.data.primary_role.label|safe }}**:
```
{{ application.data.primary_role.value|safe }}
```

{% if application.data.primary_role_other.value == "other" %}
**{{ application.data.primary_other_role.label|safe }}**:
```
{{ application.data.primary_otherrole.value|safe }}
```
{% endif %}

**{{ application.data.regular_duties.label|safe }}**
```
{{ application.data.regular_duties.value|safe }}
```

**{{ application.data.teams.label|safe }}**
```{% for team in application.data.teams.value %}
- {{ team|safe }}{% endfor %}
```

## Past Involvement

**{{ application.data.involvement.label|safe }}**
```
{{ application.data.involvement.value|safe }}
```

**{{ application.data.past_experience.label|safe }}**
```
{{ application.data.past_experience.value|safe }}
```

**{{ application.data.current_contribution.label|safe }}**
```
{{ application.data.current_contribution.value|safe }}
```

{% if application.data.current_contribution_info.value %}
**{{ application.data.current_contribution_info.label|safe }}**
```
{{ application.data.current_contribution_info.value|safe }}
```
{% endif %}

## Availability

**{{ application.data.online_availability.label|safe }}**
```
{{ application.data.online_availability.value|safe }}
```

**{{ application.data.inperson_availability.label|safe }}**
```
{{ application.data.inperson_availability.value|safe }}
```

## Additional info

**{{ application.data.public_speaking.label|safe }}**:
```
{{ application.data.public_speaking.value|default:"no response"|safe }}
```

**{{ application.data.support_needed.label|safe }}**:
```
{{ application.data.support_needed.value|default:"no response"|safe }}
```

**{{ application.data.anything_else.label|safe }}**:
```
{{ application.data.anything_else.value|default:"no response"|safe }}
```

## Conduct

**Code of Conduct agreed**:
```
True
```

**{{ application.data.not_gonna_try_to_name_this.label|safe }}**:
```
{{ application.data.not_gonna_try_to_name_this.value|safe }}
```

{% if application.data.not_gonna_try_to_name_this_info.value %}
**{{ application.data.not_gonna_try_to_name_this_info.label|safe }}**:
```
Response redacted by default. Only select PBA Admins can access this via bikeaction.org/admin/
```
{% endif %}
