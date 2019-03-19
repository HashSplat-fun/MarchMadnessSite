# MarchMadnessSite
Simple march madness bracket that lets users be grouped into teams and guess winners week by week.

==============================================================

 * clone repository
 or `pip install git+https://github.com/justengel-django/MarchMadnessSite`
   * Add to INSTALLED_APPS = ['march_madness', ...]
 * change settings
 * `python manage.py makemigrations`
 * `python manage.py migrate`
 
 ## Populate Tournament Values
 * Create a tournament with the year in the Django Admin
   * Load CSV uses the Tournament Name and Year so they must match
   * Bracket2019.csv uses "March Madness" with the Year 2019
 * `python manage.py load_csv_matches march_madness\fixtures\Bracket2019.csv`
 
  