# =====================================================
# the_school app > context_processors.py
# =====================================================

from .models import AcademicYear, SchoolSettings

def global_school_data(request):
    """
    Context processor to add global school-related data to all template contexts.

    This processor injects commonly used data such as:
    - The currently active academic year (`is_current=True`)
    - The school's general settings (name, logo, motto, etc.)
    - Accreditation details (from the related Accreditor model)

    These variables will be automatically available in all templates.
    """
    
    # ==============================================
    # Fetch Active Academic Year
    # ==============================================
    # Query to get the currently active academic year
    current_year = AcademicYear.objects.filter(is_current=True).first()

    # ==============================================
    # Fetch School Settings
    # ==============================================
    # Query to get the singleton SchoolSettings instance (only one allowed)
    school_settings = SchoolSettings.objects.first()

    # ==============================================
    # Fetch Accreditation Details
    # ==============================================
    # Retrieve all accreditation details associated with the school settings
    # If no SchoolSettings instance exists, return an empty list
    accreditation_details = school_settings.accreditation_details.all() if school_settings else []

    # ==============================================
    # Return the Data to the Template Context
    # ==============================================
    # The returned dictionary makes the data available in all templates
    return {
        'current_year': current_year,               # Active academic year
        'school_settings': school_settings,         # School general settings
        'accreditation_details': accreditation_details,  # Accreditation information
    }
