# {{ submission.submitter.first_name }} {{ submission.submitter.last_name }}

## Leader

**Name**:
```
{{ submission.submitter.first_name }} {{ submission.submitter.last_name }}
```

**District**:
```
{{ submission.submitter.profile.district }}
```

**Discord username**:
```
{{ submission.submitter.profile.discord.extra_data.username }}
```

**{{ submission.data.preferred_contact_method.label }}**:
```
{{ submission.data.preferred_contact_method.value }}
```

## Nominating Organizer/Board Member
```
{{ submission.data.nominator.value }}
```

## Desired role

**{{ submission.data.primary_role.label }}**:
```
{{ submission.data.primary_role.value }}
```

{% if submission.data.primary_role_other.value == "other" %}
**{{ submission.data.primary_other_role.label }}**:
```
{{ submission.data.primary_otherrole.value }}
```
{% endif %}

**{{ submission.data.regular_duties.label }}**
```
{{ submission.data.regular_duties.value }}
```

**{{ submission.data.teams.label }}**
```{% for team in submission.data.teams.value %}
- {{ team }}{% endfor %}
```

## Past Involvement

**{{ submission.data.involvement.label }}**
```
{{ submission.data.involvement.value }}
```

**{{ submission.data.past_experience.label }}**
```
{{ submission.data.past_experience.value }}
```

**{{ submission.data.current_contribution.label }}**
```
{{ submission.data.current_contribution.value }}
```

{% if submission.data.current_contribution_info.value %}
**{{ submission.data.current_contribution_info.label }}**
```
{{ submission.data.current_contribution_info.value }}
```
{% endif %}

## Availability

**{{ submission.data.online_availability.label }}**
```
{{ submission.data.online_availability.value }}
```

**{{ submission.data.inperson_availability.label }}**
```
{{ submission.data.inperson_availability.value }}
```

## Additional info

**{{ submission.data.public_speaking.label }}**:
```
{{ submission.data.public_speaking.value|default:"no response" }}
```

**{{ submission.data.support_needed.label }}**:
```
{{ submission.data.support_needed.value|default:"no response" }}
```

**{{ submission.data.anything_else.label }}**:
```
{{ submission.data.anything_else.value|default:"no response" }}
```

## Conduct

**Code of Conduct agreed**:
```
True
```

**{{ submission.data.not_gonna_try_to_name_this.label }}**:
```
{{ submission.data.not_gonna_try_to_name_this.value }}
```

{% if submission.data.not_gonna_try_to_name_this_info.value %}
**{{ submission.data.not_gonna_try_to_name_this_info.label }}**:
```
Response redacted by default. Only select PBA Admins can access this via bikeaction.org/admin/
```
{% endif %}
