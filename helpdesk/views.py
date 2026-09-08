from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import DatabaseYear, AuditLog
from .utils import log_action


@login_required
def database_switcher(request):
    years = DatabaseYear.objects.filter(is_active=True).order_by('-year')
    active_year = request.session.get('active_db_year', None)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'select':
            # Set the selected year as active for the current user's session
            year_id = request.POST.get('year_id')
            try:
                yr = DatabaseYear.objects.get(pk=year_id, is_active=True)
                request.session['active_db_year'] = yr.year
                request.session['active_db_name'] = yr.db_name
                messages.success(request, f'Switched active database to {yr.year} ({yr.db_name}).')
            except DatabaseYear.DoesNotExist:
                messages.error(request, 'Selected database year was not found or is inactive.')
            return redirect('database_switcher')

        elif action == 'set_default':
            # Mark all years as non-current, then set the selected year as current
            try:
                yr = DatabaseYear.objects.get(pk=request.POST.get('year_id'), is_active=True)
                DatabaseYear.objects.filter(is_current=True).update(is_current=False)
                yr.is_current = True
                yr.save()

                # Update the active session database to match
                request.session['active_db_year'] = yr.year
                request.session['active_db_name'] = yr.db_name

                log_action(
                    request,
                    AuditLog.ACTION_UPDATE,
                    'DatabaseYear',
                    str(yr.year),
                    str(yr),
                    notes=f'Set {yr.year} as default current database'
                )
                messages.success(request, f'{yr.year} ({yr.db_name}) is now set as the active current database.')
            except DatabaseYear.DoesNotExist:
                messages.error(request, 'Database year not found.')
            return redirect('database_switcher')

        elif action == 'reset':
            # Reset back to default primary database routing
            request.session.pop('active_db_year', None)
            request.session.pop('active_db_name', None)
            messages.info(request, 'Returned to default active database.')
            return redirect('database_switcher')

    current_yr_obj = DatabaseYear.objects.filter(is_current=True).first()

    return render(request, 'helpdesk/database_switcher.html', {
        'years': years,
        'active_year': active_year,
        'current_year_obj': current_yr_obj,
    })