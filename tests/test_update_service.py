def test_check_new_files_and_send_email(update_service, old_files, mocker):
    # Mock scraper
    mocker.patch.object(
        update_service.scraper,
        'get_file_list',
        return_value=old_files
    )
    
    # Mock db handler
    mocker.patch.object(
        update_service.db_handler,
        'get_last_scraper_result',
        return_value=old_files[1:]  # Return all but first file
    )
    mocker.patch.object(
        update_service.db_handler,
        'save_scraper_result',
        return_value=True
    )
    
    # Mock email sender
    mock_send_email = mocker.patch.object(
        update_service.email_sender,
        'send_new_file_email',
        return_value=True
    )
    
    # Run the service
    update_service.check_new_files_and_send_email()
    
    # Verify email was sent with new file
    mock_send_email.assert_called_once()
    sent_files = mock_send_email.call_args[0][0]
    assert len(sent_files) == 1
    assert sent_files[0]['filename'] == old_files[0]['filename']

def test_no_new_files(update_service, old_files, mocker):
    # Mock scraper and db to return same files
    mocker.patch.object(
        update_service.scraper,
        'get_file_list',
        return_value=old_files
    )
    mocker.patch.object(
        update_service.db_handler,
        'get_last_scraper_result',
        return_value=old_files
    )
    
    # Mock email sender
    mock_send_email = mocker.patch.object(
        update_service.email_sender,
        'send_new_file_email',
        return_value=True
    )
    
    # Run the service
    update_service.check_new_files_and_send_email()
    
    # Verify no email was sent
    mock_send_email.assert_not_called()

def test_compare_files_to_get_new(update_service, current_files, old_files):
    new_files = update_service._compare_files_to_get_new(current_files, old_files)
    assert len(new_files) == 1
    assert new_files[0]['filename'] == current_files[0]['filename']

def test_check_new_files_and_send_email_error(update_service):
    update_service.check_new_files_and_send_email()
    assert update_service.scraper.get_file_list.call_count == 1
    assert update_service.db_handler.save_scraper_result.call_count == 1


