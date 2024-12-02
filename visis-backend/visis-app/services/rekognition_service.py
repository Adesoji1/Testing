# services/rekognition_service.py

# import boto3
# import logging
# from botocore.exceptions import BotoCoreError, ClientError

# logger = logging.getLogger(__name__)

# class RekognitionService:
#     def __init__(self, region_name: str = 'us-east-1'):
#         self.rekognition_client = boto3.client('rekognition', region_name=region_name)

#     def detect_labels(self, bucket_name: str, file_key: str) -> str:
#         """Detect labels in the image using AWS Rekognition."""
#         try:
#             response = self.rekognition_client.detect_labels(
#                 Image={
#                     'S3Object': {
#                         'Bucket': bucket_name,
#                         'Name': file_key,
#                     }
#                 },
#                 MaxLabels=10,
#                 MinConfidence=70,
#             )
#             labels = response['Labels']
#             if not labels:
#                 return "No objects or scenes detected."
#             description = "This image may contain: " + ', '.join([label['Name'] for label in labels])
#             logger.info(f"Rekognition labels detected: {description}")
#             return description
#         except (BotoCoreError, ClientError) as e:
#             logger.error(f"AWS Rekognition error: {str(e)}")
#             raise e




# services/rekognition_service.py

import boto3
import logging
import nltk
import random
from typing import List, Dict
from botocore.exceptions import BotoCoreError, ClientError
from nltk.corpus import wordnet

logger = logging.getLogger(__name__)

class RekognitionService:
    def __init__(self, region_name: str = 'us-east-1'):
        self.rekognition_client = boto3.client('rekognition', region_name=region_name)
        # Download necessary NLTK data (only need to run once)
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)

    def detect_labels(self, bucket_name: str, file_key: str) -> str:
        """Detect labels in the image using AWS Rekognition and generate a description."""
        try:
            response = self.rekognition_client.detect_labels(
                Image={
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name': file_key,
                    }
                },
                MaxLabels=10,
                MinConfidence=70,
            )
            labels = response['Labels']
            if not labels:
                return "No objects or scenes detected."

            # Generate a natural language description
            description = self.generate_description(labels)
            logger.info(f"Generated description: {description}")
            return description
        except (BotoCoreError, ClientError) as e:
            logger.error(f"AWS Rekognition error: {str(e)}")
            raise e

    def generate_description(self, labels: List[Dict]) -> str:
        """Generate a natural language description from Rekognition labels."""
        # Extract label names and sort by confidence
        label_names = [label['Name'] for label in sorted(labels, key=lambda x: x['Confidence'], reverse=True)]

        if not label_names:
            return "No objects or scenes detected."

        # Use NLTK to generate a description
        description = self.construct_sentence(label_names)
        return description

    def construct_sentence(self, label_names: List[str]) -> str:
        """Construct a natural language sentence from label names using custom templates and synonyms."""
        templates = [
            "This image appears to show {}.",
            "You can see {} in this picture.",
            "The photo likely contains {}.",
            "It seems that there are {} in this image.",
            "This picture displays {}.",
        ]
        template = random.choice(templates)

        # Generate a list of synonyms for each label
        all_synonyms = []
        for label in label_names:
            synonyms = self.get_synonyms(label)
            # Choose one synonym randomly or use the label itself
            synonym = random.choice(synonyms) if synonyms else label.lower()
            all_synonyms.append(synonym)

        # Remove duplicates while preserving order
        unique_synonyms = []
        [unique_synonyms.append(x) for x in all_synonyms if x not in unique_synonyms]

        # Construct the items string
        if len(unique_synonyms) == 1:
            items = unique_synonyms[0]
        else:
            items = ', '.join(unique_synonyms[:-1]) + ', and ' + unique_synonyms[-1]

        # Format the sentence
        sentence = template.format(items)
        return sentence.capitalize()

    def get_synonyms(self, word: str) -> List[str]:
        """Get a list of synonyms for a given word using NLTK's WordNet."""
        synonyms = set()
        for syn in wordnet.synsets(word, pos=wordnet.NOUN):
            for lemma in syn.lemmas():
                synonym = lemma.name().replace('_', ' ')
                synonyms.add(synonym.lower())
        # Exclude the original word from the synonyms
        synonyms.discard(word.lower())
        return list(synonyms)
