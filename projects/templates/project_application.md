# {{ application.data.shortname.value|safe }}

> {{ application.data.quick_summary.value|safe }}

## Leader

**Name**:
> {{ application.submitter.first_name }} {{ application.submitter.last_name }}

**Discord username**:
> {{ application.submitter.profile.discord.extra_data.username }}

**{{ application.data.leader_preferred_contact_method.label }}**:
> {{ application.data.leader_preferred_contact_method.value }}

**Past Experience**:
> {{ application.data.leader_past_experience.value|safe }}

## Overview

**{{ application.data.mission_relevance.label|safe }}**:
> {{ application.data.mission_relevance.value|safe }}

**{{ application.data.success_criteria.label|safe }}**:
> {{ application.data.success_criteria.value|safe }}

**{{ application.data.name_use.label|safe }}**:
> {{ application.data.name_use.value|safe }}

**{{ application.data.recruitment.label|safe }}**:
> {{ application.data.recruitment.value|safe }}

**{{ application.data.external_orgs.label|safe }}**:
> {{ application.data.external_orgs.value|safe }}

## Logistics

**{{ application.data.location.label|safe }}**:
> {% if application.data.location.value %}{{ application.data.location.value|safe }}{% else %}no response{% endif %}

**{{ application.data.time_and_date.label|safe }}**:
> {% if application.data.time_and_date.value %}{{ application.data.time_and_date.value|safe }}{% else %}no response{% endif %}

**{{ application.data.recurring.label|safe }}**:
> {% if application.data.recurring.value %}{{ application.data.recurring.value|safe }}{% else %}no response{% endif %}

## Resources

**{{ application.data.equipment_needed.label|safe }}**:
> {{ application.data.equipment_needed.value|safe }}

**{{ application.data.volunteers_needed.label|safe }}**:
> {{ application.data.volunteers_needed.value|safe }}

**{{ application.data.promotion_needed.label|safe }}**:
> {{ application.data.promotion_needed.value|safe }}

**{{ application.data.finances_needed.label|safe }}**:
> {{ application.data.finances_needed.value|safe }}

**{{ application.data.others_needed.label|safe }}**:
> {% if application.data.others_needed.value %}{{ application.data.others_needed.value|safe }}{% else %}no response{% endif %}

## Anything Else

**{{ application.data.anything_else.label|safe }}**:
> {% if application.data.anything_else.value %}{{ application.data.anything_else.value|safe }}{% else %}no response{% endif %}
