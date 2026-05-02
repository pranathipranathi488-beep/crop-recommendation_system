import os
import re

directory = 'templates'

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace Jinja2 flash messages with Django messages
            pattern = r'\{%\s*with\s+messages\s*=\s*get_flashed_messages\(.*?\)\s*%\}(.*?)\{%\s*endwith\s*%\}'
            replacement = r'''{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert" style="position: absolute; top: 100px; right: 20px; z-index: 1000; padding: 15px; border-radius: 8px; background: rgba(255,255,255,0.9); color: #000;">
            {{ message }}
        </div>
    {% endfor %}
{% endif %}'''
            
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {filepath}")
