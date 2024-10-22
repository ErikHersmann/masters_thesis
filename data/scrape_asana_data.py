import asana, json, random
# from asana.rest import ApiException
# from pprint import pprint
from pathlib import Path
from datetime import datetime
from math import ceil

random.seed(7)


with open(
    str(Path(__file__).parent.parent.absolute().as_posix()) + "/resources/config.json"
) as f: 
    environment = json.load(f)
configuration = asana.Configuration()
configuration.access_token = environment["access_token"]
api_client = asana.ApiClient(configuration)

skill_lb, skill_ub = (
    environment["skill_config"]["min_job_requirement"],
    environment["skill_config"]["max_job_requirement"],
)

# create an instance of the API class
projects_api_instance = asana.ProjectsApi(api_client)
workspace_gid = environment["workspace"]
# str | Globally unique identifier for the workspace or organization.
opts = {
    "limit": 50,  # int | Results per page. The number of objects to return per page. The value must be between 1 and 100.
    "archived": False,  # bool | Only return projects whose `archived` field takes on the value of this parameter.
}

api_response = projects_api_instance.get_projects_for_workspace(workspace_gid, opts)
tasks_api_instance = asana.TasksApi(api_client)
opts = {
    "limit": 50,  # int | Results per page. The number of objects to return per page. The value must be between 1 and 100.
    "project": "",  # str | The project to filter tasks on.
    "opt_fields": "actual_time_minutes,approval_status,assignee,assignee.name,assignee_section,assignee_section.name,assignee_status,completed,completed_at,completed_by,completed_by.name,created_at,created_by,custom_fields,custom_fields.asana_created_field,custom_fields.created_by,custom_fields.created_by.name,custom_fields.currency_code,custom_fields.custom_label,custom_fields.custom_label_position,custom_fields.date_value,custom_fields.date_value.date,custom_fields.date_value.date_time,custom_fields.description,custom_fields.display_value,custom_fields.enabled,custom_fields.enum_options,custom_fields.enum_options.color,custom_fields.enum_options.enabled,custom_fields.enum_options.name,custom_fields.enum_value,custom_fields.enum_value.color,custom_fields.enum_value.enabled,custom_fields.enum_value.name,custom_fields.format,custom_fields.has_notifications_enabled,custom_fields.id_prefix,custom_fields.is_formula_field,custom_fields.is_global_to_workspace,custom_fields.is_value_read_only,custom_fields.multi_enum_values,custom_fields.multi_enum_values.color,custom_fields.multi_enum_values.enabled,custom_fields.multi_enum_values.name,custom_fields.name,custom_fields.number_value,custom_fields.people_value,custom_fields.people_value.name,custom_fields.precision,custom_fields.representation_type,custom_fields.resource_subtype,custom_fields.text_value,custom_fields.type,dependencies,dependents,due_at,due_on,external,external.data,followers,followers.name,hearted,hearts,hearts.user,hearts.user.name,html_notes,is_rendered_as_separator,liked,likes,likes.user,likes.user.name,memberships,memberships.project,memberships.project.name,memberships.section,memberships.section.name,modified_at,name,notes,num_hearts,num_likes,num_subtasks,offset,parent,parent.created_by,parent.name,parent.resource_subtype,path,permalink_url,projects,projects.name,resource_subtype,start_at,start_on,tags,tags.name,uri,workspace,workspace.name",  # list[str] | This endpoint returns a compact resource, which excludes some properties by default. To include those optional properties, set this query parameter to a comma-separated list of the properties you wish to include.
}

jobs = []
job_index = 0

for data in api_response:
    opts["project"] = data["gid"]
    api_response = tasks_api_instance.get_tasks(opts)
    for task in api_response:
        # pprint(task)
        if not task['due_on'] or not task['created_at']:
            continue
        deadline = days_difference = (
            datetime.strptime(task["due_on"], "%Y-%m-%d").date()
            - datetime.strptime(task["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").date()
        ).days
        if deadline <= 0:
            # Bad values
            continue    
        task_name = task["name"]

        # Trying to find the skills
        found = False
        for skill_name_idx, skill_name in enumerate(environment['skills']):
            if skill_name in task_name:
                required_skill = skill_name_idx
                found = True
                break

        if not found:
            required_skill = random.randint(0, len(environment["skills"]) - 1)

        task_duration = 0
        for custom_field in task["custom_fields"]:
            if custom_field["name"] == "Zeitbedarf (h)" and custom_field['number_value']:
                task_duration = ceil(float(custom_field['number_value']))
                break
        if task_duration <= 0:
            continue
        #    task_duration = random.randint(1, deadline)

        jobs.append(
            {
                "skill_required": required_skill,
                "skill_level_required": random.randint(skill_lb, skill_ub),
                "base_duration": task_duration,
                "deadline": deadline * 8, # This is because due dates are in days but required time is in hours
                "index": job_index,
                "name": task_name,
                "type": "job",
            }
        )
        # print(f"{jobs[-1]}")
        job_index += 1
print(f"Scraped {len(jobs)} jobs from asana")


skill_count = len(environment['skills'])
for skill_idx in range(skill_count):
    jobs.append(
        {
            "skill_required": skill_idx,
            "skill_level_required": 0,
            "base_duration": 5,
            "deadline": None,
            "index": job_index + skill_idx,
            "name": f"{environment['skills'][skill_idx]}-seminar",
            "skill_improvement_baseline": 5,
            "type": "seminar",
        }
    )
print(f"Added {skill_count} seminars")

with open('output/asana_jobs.json', "w", encoding="utf-8") as f:
    json.dump(jobs, f)