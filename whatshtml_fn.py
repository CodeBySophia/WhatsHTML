from PySide6 import QtWidgets
import re
import os
from jinja2 import Template
import shutil
from functools import partial
from urllib.parse import urlparse  # for processing URLs

# Allowed file types for attachments
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
AUDIO_EXTENSIONS = {"ogg", "amr", "3gp", "aac", "mpeg", "opus"}
VIDEO_EXTENSIONS = {"mp4"}
DOCUMENT_EXTENSIONS = {"pdf", "doc", "docx", "pptx", "xlsx"}
CONTACT_EXTENSIONS = {"vcf"}

participant_settings = {}
primary_participant = None  # Global variable to store the primary (first) participant

# Main function to export text messages and attachments to HTML file
def process_files(txt_file, attachment_files, temp_dir):
    # Prompt user for export name
    export_name = get_export_name()
    if not export_name:
        return

    # Create output directories
    output_dir = os.path.join(os.getcwd(), export_name)
    os.makedirs(output_dir, exist_ok=True)
    output_html = os.path.join(output_dir, f"{export_name}.html")
    attachments_folder = os.path.join(output_dir, "attachments")
    os.makedirs(attachments_folder, exist_ok=True)

    # Parse chat and detect participants
    chat_messages, participants = parse_chat(txt_file)

    # Setup participant configuration (now works with more than two participants)
    setup_participant_settings(participants)
    apply_renamed_participants(chat_messages)

    # Categorize external attachment files and copy them to export folder
    categorized_files = categorize_files(attachment_files, attachments_folder)
    shutil.copy(txt_file, os.path.join(attachments_folder, os.path.basename(txt_file)))

    # Process inline attachments within messages (images, audio, video, documents)
    process_message_attachments(chat_messages, attachments_folder)

    # Process URLs in messages to display shortened links with preview
    process_urls_in_messages(chat_messages)

    # Generate HTML export (export name is passed for the header)
    generate_html(chat_messages, output_html, export_name)
    
    # Clean up temporary extracted files
    shutil.rmtree(temp_dir)

# Categorize external files (attachments) and copy them to target folder
def categorize_files(files, target_folder):
    categorized = {"images": [], "audio": [], "video": [], "documents": [], "contacts": []}
    for file in files:
        ext = file.split(".")[-1].lower()
        target_path = os.path.join(target_folder, os.path.basename(file))
        shutil.copy(file, target_path)
        if ext in IMAGE_EXTENSIONS:
            categorized["images"].append(target_path)
        elif ext in AUDIO_EXTENSIONS:
            categorized["audio"].append(target_path)
        elif ext in VIDEO_EXTENSIONS:
            categorized["video"].append(target_path)
        elif ext in DOCUMENT_EXTENSIONS:
            categorized["documents"].append(target_path)
        elif ext in CONTACT_EXTENSIONS:
            categorized["contacts"].append(target_path)
    return categorized

def get_export_name():
    # Prompt user for export name
    dialog = QtWidgets.QInputDialog()
    dialog.setWindowTitle("Export Name")
    dialog.setLabelText("Zadej název exportu:")
    dialog.setTextValue("chat_export")
    if dialog.exec() == QtWidgets.QDialog.Accepted:
        return dialog.textValue()
    return None

def parse_chat(file_path):
    # Parse chat text into messages and detect participants
    pattern = re.compile(r"(\d{2}\.\d{2}\.\d{2} \d{1,2}:\d{2}) - (.+?): (.+)")
    messages = []
    participants = set()
    current_message = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            match = pattern.match(line)
            if match:
                # Save previous message if exists
                if current_message:
                    messages.append(current_message)
                timestamp, sender, content = match.groups()
                current_message = {
                    'timestamp': timestamp,
                    'sender': sender,
                    'content': content
                }
                participants.add(sender)
            elif current_message:
                # Append additional lines to the current message
                current_message['content'] += ' ' + line

        if current_message:
            messages.append(current_message)

    return messages, list(participants)

# Process inline attachments in messages (images, audio, video, documents)
def process_message_attachments(messages, attachments_folder):
    # Regex to match a filename with allowed extensions (case insensitive)
    attachment_regex = re.compile(
        r"([\w\-.]+\.(?:jpg|jpeg|png|webp|ogg|amr|3gp|aac|mpeg|opus|mp4|pdf|doc|docx|pptx|xlsx|vcf))",
        re.IGNORECASE
    )
    for message in messages:
        content = message['content']
        if "(soubor byl přiložen)" in content:
            # Remove the attachment phrase from message content
            message['content'] = content.replace("(soubor byl přiložen)", "").strip()
            match = attachment_regex.search(message['content'])
            if match:
                filename = match.group(1)
                ext = filename.split(".")[-1].lower()
                # Determine attachment type based on extension
                if ext in IMAGE_EXTENSIONS:
                    attachment_type = 'image'
                elif ext in AUDIO_EXTENSIONS:
                    attachment_type = 'audio'
                elif ext in VIDEO_EXTENSIONS:
                    attachment_type = 'video'
                else:
                    attachment_type = 'document'
                message['attachment'] = {
                    'filename': filename,
                    'type': attachment_type,
                    'path': os.path.join("attachments", filename)  # relative path for HTML
                }
                # Remove the filename from the message content if present
                message['content'] = message['content'].replace(filename, "").strip()
            else:
                message['attachment'] = None
        else:
            message['attachment'] = None

# Process URLs in message content to display shortened links with preview similar to WhatsApp
def process_urls_in_messages(messages):
    url_regex = re.compile(r'(https?://[^\s]+)')
    for message in messages:
        def replace_url(match):
            url = match.group(0)
            parsed = urlparse(url)
            # Show only the domain name (page title) as the link text
            display_text = parsed.netloc
            favicon_url = f"https://www.google.com/s2/favicons?sz=64&domain_url={url}"
            return (f'<div class="link-preview">'
                    f'<img src="{favicon_url}" alt="Preview">'
                    f'<div class="link-info">'
                    f'<a href="{url}" target="_blank" title="{url}">{display_text}</a>'
                    f'</div></div>')
        message['content'] = url_regex.sub(replace_url, message['content'])

# Generate HTML export with header (export name) and styling for chat bubbles and link previews
def generate_html(messages, output_file, export_name):
    template_str = """
    <!DOCTYPE html>
    <html lang="cs">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chat Export</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f7f7f7; padding: 20px; }
            .chat-container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            /* Header using export name */
            .header { text-align: center; margin-bottom: 20px; }
            .header h1 { margin: 0; font-size: 2em; }
            .message { margin-bottom: 15px; padding: 10px; border-radius: 8px; max-width: 66.66%; word-wrap: break-word; }
            .timestamp { font-size: 0.8em; color: #555; } /* darker color for timestamp */
            .sender { font-size: 0.9em; font-weight: bold; margin-bottom: 5px; }
            .attachment { margin-top: 10px; }
            /* Images and videos in chat bubbles: max one third of window width */ 
            .attachment img, .attachment video { max-width: 33%; height: auto; cursor: pointer; border-radius: 8px; }
            /* Modal styles for image popup */
            .modal { display: none; position: fixed; z-index: 1; padding-top: 100px; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.9); }
            .modal-content { margin: auto; display: block; max-width: 90%; }
            .close { position: absolute; top: 50px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; cursor: pointer; }
            /* Link preview styling similar to WhatsApp */
            .link-preview { display: flex; align-items: center; border: 1px solid #ccc; padding: 5px; border-radius: 6px; margin-top: 5px; max-width: 100%; }
            .link-preview img { width: 40px; height: 40px; margin-right: 10px; }
            .link-preview .link-info { display: flex; flex-direction: column; }
            .link-preview .link-info a { font-weight: bold; color: #0645ad; text-decoration: none; }
            .link-preview .link-info a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <!-- Header with export name -->
            <div class="header">
                <h1>{{ export_name }}</h1>
            </div>
            {% for message in messages %}
                <div class="message" style="background-color: {{ message.color }}; text-align: {{ 'right' if message.is_right else 'left' }}; {{ 'margin-left: auto;' if message.is_right else 'margin-right: auto;' }}">
                    <div class="timestamp">{{ message.timestamp }}</div>
                    <div class="sender">{{ message.sender }}</div>
                    <div class="content">{{ message.content | safe }}</div>
                    {% if message.attachment %}
                        <div class="attachment">
                        {% if message.attachment.type == 'image' %}
                            <img src="{{ message.attachment.path }}" alt="Image">
                        {% elif message.attachment.type == 'audio' %}
                            <audio controls>
                                <source src="{{ message.attachment.path }}" type="{% if message.attachment.filename.split('.')[-1].lower() == 'opus' %}audio/ogg; codecs=opus{% else %}audio/{{ message.attachment.filename.split('.')[-1].lower() }}{% endif %}">
                                Your browser does not support the audio element.
                            </audio>
                        {% elif message.attachment.type == 'video' %}
                            <a href="{{ message.attachment.path }}" target="_blank">
                                <video controls>
                                    <source src="{{ message.attachment.path }}" type="video/mp4">
                                    Your browser does not support the video tag.
                                </video>
                            </a>
                        {% else %}
                            <a href="{{ message.attachment.path }}">Open attachment ({{ message.attachment.filename }})</a>
                        {% endif %}
                        </div>
                    {% endif %}
                </div>
            {% endfor %}
        </div>
        
        <!-- Modal for image popup -->
        <div id="imgModal" class="modal">
          <span class="close">&times;</span>
          <img class="modal-content" id="modalImg">
        </div>
        
        <script>
            // Get the modal
            var modal = document.getElementById("imgModal");
            var modalImg = document.getElementById("modalImg");
            // Attach click event to all images in attachments
            document.querySelectorAll(".attachment img").forEach(function(img) {
                img.onclick = function(){
                    modal.style.display = "block";
                    modalImg.src = this.src;
                }
            });
            // Get the <span> element that closes the modal
            var span = document.getElementsByClassName("close")[0];
            span.onclick = function() { modal.style.display = "none"; }
        </script>
    </body>
    </html>
    """
    template = Template(template_str)
    html_content = template.render(messages=messages, export_name=export_name)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    # Show success dialog with export location
    success_dialog = QtWidgets.QMessageBox()
    success_dialog.setWindowTitle("Export Complete")
    success_dialog.setText(f"Chat export was successfully generated: {output_file}")
    success_dialog.setIcon(QtWidgets.QMessageBox.Information)
    success_dialog.exec()

def setup_participant_settings(participants):
    global participant_settings, primary_participant
    # Initialize participant settings with default values
    participant_settings = {participant: {'name': participant, 'color': None} for participant in participants}

    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle("Nastavení účastníků")
    layout = QtWidgets.QVBoxLayout()

    rename_fields = {}
    color_widgets = {}

    for participant in participants:
        group = QtWidgets.QGroupBox(f"Nastavení pro {participant}")
        group_layout = QtWidgets.QFormLayout()

        # Field for renaming participant
        rename_field = QtWidgets.QLineEdit(participant)
        group_layout.addRow("Jméno:", rename_field)
        rename_fields[participant] = rename_field

        # Color selection for participant
        color_label = QtWidgets.QLabel("Žádná barva")
        color_button = QtWidgets.QPushButton("Vyber barvu")
        color_button.clicked.connect(partial(choose_color, color_label, participant))
        group_layout.addRow("Barva:", color_button)
        group_layout.addRow("Vybraná barva:", color_label)
        color_widgets[participant] = color_label

        group.setLayout(group_layout)
        layout.addWidget(group)

    # OK and Cancel buttons for the dialog
    button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)

    dialog.setLayout(layout)
    if dialog.exec():
        # Update participant settings with user input
        for participant in participants:
            participant_settings[participant].update({
                'name': rename_fields[participant].text(),
                'color': color_widgets[participant].text() if color_widgets[participant].text() != "Žádná barva" else None
            })
        # Now show a separate dialog for primary participant selection
        select_primary_participant()

def select_primary_participant():
    global primary_participant
    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle("Výběr primárního účastníka")
    layout = QtWidgets.QVBoxLayout()
    label = QtWidgets.QLabel("Vyber primárního účastníka (bubliny vlevo):")
    combo = QtWidgets.QComboBox()
    # Add current names of participants in the combo box
    for p in participant_settings.values():
        combo.addItem(p['name'])
    layout.addWidget(label)
    layout.addWidget(combo)
    button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)
    dialog.setLayout(layout)
    if dialog.exec():
        primary_participant = combo.currentText()

def apply_renamed_participants(messages):
    global primary_participant
    # Use the selected primary participant for alignment
    if primary_participant is None:
        primary = list(participant_settings.keys())[0]
    else:
        primary = primary_participant
    for message in messages:
        original_sender = message['sender']
        if original_sender in participant_settings:
            settings = participant_settings[original_sender]
            message['sender'] = settings['name']
            message['is_right'] = (settings['name'] != primary)
            message['color'] = settings['color'] if settings['color'] is not None else (
                '#add8e6' if settings['name'] == primary else '#90ee90'
            )
        else:
            message['is_right'] = True
            message['color'] = '#90ee90'

def choose_color(label, participant):
    global participant_settings
    color = QtWidgets.QColorDialog.getColor()
    if color.isValid():
        label.setText(color.name())
        participant_settings[participant]['color'] = color.name()