'Win Excel Range to File
'--------------------------------------------------------------
 Set oShell = CreateObject("WScript.Shell")
 Set ofso = CreateObject("Scripting.FileSystemObject")
 dirScript = oFSO.GetParentFolderName(WScript.ScriptFullName)
 Call Replace(dirScript,WScript.ScriptName,"")
'--------------------------------------------------------------
out_file = dirScript & "\" & "dart_output.txt"
excel_file = dirScript & "\" & "dart_message_generator.xlsx"
row1=28
row2=228
'--------------------------------------------------------------
rows=row2-row1+1

Set objExcel = CreateObject("Excel.Application")
Set objWorkbook = objExcel.Workbooks.Open( excel_file )

objExcel.Application.Visible = True

objExcel.ActiveWorkbook.Sheets("dart_out").Select 
objWorkbook.Activesheet.Range("A28:A228").Select

dim ss
ss = objWorkbook.Activesheet.Range("A28:A228").Value

Set objFSO=CreateObject("Scripting.FileSystemObject")
Set objFile = objFSO.CreateTextFile(out_file,True)

For i = 1 To rows
   objFile.Write ss(1,1) & vbCrLf
Next
objFile.Close


objExcel.Application.Quit
WScript.Echo "Finished."
WScript.Quit

