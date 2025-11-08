# backend/api/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Dataset
from .serializers import DatasetSerializer
import pandas as pd
from django.core.files.storage import default_storage

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .pdf_generator import generate_summary_pdf


class DatasetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows datasets to be viewed or created.
    """

    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

    def list(self, request, *args, **kwargs):
        """
        Custom LIST action: Only return the 5 most recent datasets.
        """
        queryset = Dataset.objects.all().order_by("-uploaded_at")[:5]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Custom CREATE action: Handle file upload and analysis.
        """
        # 1. Get the file from the request
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Save the dataset object (without summary) to get a file path
        # We also get the filename to use as the 'name'
        dataset_name = file_obj.name
        dataset = Dataset(file=file_obj, name=dataset_name)
        dataset.save()

        # --- REPLACE WITH THIS ---
        try:
            # 3. Open the saved file with Pandas using its direct path
            # This is more reliable than using default_storage.open()
            df = pd.read_csv(dataset.file.path)

            # 4. Perform analytics (as required by the task)
            total_count = len(df)

            # Ensure numeric conversion, handling errors
            numeric_cols = ["Flowrate", "Pressure", "Temperature"]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Calculate averages, handling potential empty/NaN data
            averages = {
                "avg_flowrate": df["Flowrate"].mean(skipna=True),
                "avg_pressure": df["Pressure"].mean(skipna=True),
                "avg_temperature": df["Temperature"].mean(skipna=True),
            }

            # Equipment type distribution
            type_distribution = df["Type"].value_counts().to_dict()

            # 5. Create the summary JSON
            summary = {
                "total_count": total_count,
                "averages": averages,
                "type_distribution": type_distribution,
                "columns": list(df.columns),  # Also send column names
                "first_5_rows": df.head(5).to_dict("records"),  # And a sample
            }

            # 6. Save the summary to the dataset object
            dataset.summary = summary
            dataset.save()

            # 7. History Management: Delete oldest if > 5
            self.enforce_dataset_limit()

            # 8. Send the successful response back
            serializer = self.get_serializer(dataset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # If analysis fails, delete the corrupt dataset object
            dataset.delete()
            return Response(
                {"error": f"Failed to process file: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def enforce_dataset_limit(self):
        """
        Deletes the oldest datasets if the count exceeds 5.
        """
        all_datasets = Dataset.objects.all().order_by("-uploaded_at")
        if all_datasets.count() > 5:
            # Get IDs of datasets to delete
            ids_to_delete = all_datasets[5:].values_list("id", flat=True)

            # Delete the corresponding files from storage first
            for old_dataset in Dataset.objects.filter(id__in=ids_to_delete):
                try:
                    default_storage.delete(old_dataset.file.name)
                except Exception as e:
                    # Log this error in a real app
                    print(f"Error deleting file {old_dataset.file.name}: {e}")

            Dataset.objects.filter(id__in=ids_to_delete).delete()


# backend/api/views.py

# ... (at the very bottom, after DatasetViewSet) ...


class DatasetPDFDownloadView(APIView):
    """
    A view to download a PDF summary for a specific dataset.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            # 1. Get the dataset object
            dataset = Dataset.objects.get(pk=pk)

            # 2. Check if this dataset belongs to the user
            #    (In a real app, you'd check ownership. For this,
            #    we'll just let any authenticated user download.)

            # 3. Generate the PDF bytes
            pdf_bytes = generate_summary_pdf(dataset)

            # 4. Create the HTTP response
            response = HttpResponse(pdf_bytes, content_type="application/pdf")
            # This header tells the browser to download the file
            response["Content-Disposition"] = (
                f'attachment; filename="{dataset.name}_summary.pdf"'
            )

            return response

        except Dataset.DoesNotExist:
            return Response(
                {"error": "Dataset not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to generate PDF: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
