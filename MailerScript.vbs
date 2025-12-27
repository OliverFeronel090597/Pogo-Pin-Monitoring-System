
Set Outlook = CreateObject("Outlook.Application")
Set Mail = Outlook.CreateItem(0)

With Mail
    .To = "marfrey.oligario@ams-osram.com"
    .Subject = "Test Subject"
    .Body = "Hello Marfrey," & vbCrLf & "" & vbCrLf & "This is a test mail from Python via VBS in current path."
    .Display
End With
