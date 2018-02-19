import gitlab
import sys
import json

class SwaggerTest:

    def __init__(self, swagger = None, repo = None):
        self.gl = gitlab.Gitlab.from_config('psi_external', ['./gitlab.cfg'])
        self.gl.auth()
        self.project = self.gl.projects.get(repo)
        if self.project is not None:
            self.swagger = self.read_swagger(swagger)

    def read_swagger(self, path):
        with open(path, 'r') as json_file:
            return json.load(json_file)

    def delete_issues(self, term=None):
        issues = self.project.issues.list(state='opened', per_page=100)
        found = False
        for issue in issues:
            print(issue.title)
            if term and term in issue.title:
                found = True
                issue.state_event = 'close'
                issue.save()
        if found:
            self.delete_issues(term)

    def parse_swagger(self):
        count = 0
        for entry in self.swagger['paths']:
            desc_text = "{}\n".format(entry)
            methods = self.swagger['paths'][entry]
            for key in methods:
                url = "{}{}".format(self.swagger['basePath'], entry)
                desc_text += """\nURL to test: {}. 
                Parameters: {} 
                Purpose: {} """.format(url, methods[key]['parameters'], methods[key]['summary'])
            issue = {
                'title': '[TO TEST] {} - {}'.format(key.upper(), entry),
                'description': desc_text,
                'labels': ['testing', 'e2e']
                }
            print(issue)
            count += 1
            print(count)
            existing_issues = self.project.issues.list(search=issue['title'])
            if existing_issues is not None and len(existing_issues) == 0:
                print('Creating {}'.format(issue['title']))
                #self.project.issues.create(issue)
            else:
                print('Issue already exists')
            print('-----')



if len(sys.argv) != 2:
    s = SwaggerTest(sys.argv[1], sys.argv[2])
#    s.delete_issues()
    s.parse_swagger()
else:
    print('Usage: swagger_test.py <SWAGGER PATH> <GROUP/REPO>')


