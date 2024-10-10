import os
import re
import time
import schedule
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta

# Set up OAuth 2.0 credentials and API client
def get_authenticated_service():
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "../client_secrets.json"
    
    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file,
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials
    )
    return youtube

# Upload video function
def upload_video(youtube, video_file, title, description, tags, category_id="20", privacy_status="private"):
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy_status
            }
        },
        media_body=MediaFileUpload(video_file)
    )
    response = request.execute()
    print(f"Uploaded video: {title}")
    return response['id']

# Make video public function
def make_video_public(youtube, video_id):
    request = youtube.videos().update(
        part="status",
        body={
            "id": video_id,
            "status": {
                "privacyStatus": "public"
            }
        }
    )
    response = request.execute()
    print(f"Video {video_id} is now public")

# Custom sorting function to extract numbers inside parentheses
def get_number_from_filename(filename):
    match = re.search(r'\((\d+)\)', filename)
    if match:
        return int(match.group(1))  # Extract the number inside parentheses
    return float('inf')  # If no number is found, place it at the end

# Function to list and sort video files by number inside parentheses
def get_sorted_video_files(folder_path):
    # Define the video naming pattern you're looking for
    patterns = ["ACE", "4K", "3K", "1v5", "1v4", "1v3", "1v2"]

    # Get all files in the folder
    files = [f for f in os.listdir(folder_path) if f.endswith(('.mp4', '.mkv', '.mov'))]
    
    # Sort by the number inside parentheses and by file pattern
    sorted_files = []
    for pattern in patterns:
        # Find all files that match the current pattern
        matching_files = [f for f in files if f.startswith(pattern)]
        # Sort those files by the number inside parentheses
        matching_files.sort(key=get_number_from_filename)
        # Add sorted files to the final list
        sorted_files.extend(matching_files)
    
    return sorted_files

# Upload and schedule function
def handle_upload_and_schedule(folder_path):
    youtube = get_authenticated_service()

    # Get sorted list of video files
    video_files = get_sorted_video_files(folder_path)

    for idx, video_file in enumerate(video_files):
        full_path = os.path.join(folder_path, video_file)
        # Generate a title, description, and tags from file name or use static ones
        title = f"{video_file}"
        description = f"Description for {video_file}"
        tags = ["gaming", "video", "valorant", "clutch", "shooter", "fps", "highlights"]

        # Upload the video
        video_id = upload_video(youtube, full_path, title, description, tags)

        # Schedule video to go public on the next day
        schedule_time = datetime.now() + timedelta(days=idx + 1)
        schedule_time_str = schedule_time.strftime("%H:%M:%S")
        schedule.every().day.at(schedule_time_str).do(make_video_public, youtube=youtube, video_id=video_id)
        print(f"Scheduled {video_file} to go public at {schedule_time_str}")

# Main entry to start the process
if __name__ == "__main__":
    # Path to the folder containing the videos
    folder_path = "/path/to/your/videos/folder"
    
    # Start uploading and scheduling
    # handle_upload_and_schedule(folder_path)
    sorted_videos = get_sorted_video_files(folder_path)
    print(sorted_videos)

    # Keep the script running to check the schedule
    '''
    while True:
        schedule.run_pending()
        time.sleep(60)
    '''
