' Launch THIS WORKTREE's PromptCrafter, for judging a branch before it lands.
' Same shape as the pinned shortcut, with the three things a worktree needs
' done differently:
'   - it borrows the primary checkout's .venv (a worktree has none of its own;
'     the primary is three levels up: <primary>\.claude\worktrees\<name>),
'     falling back to python on PATH exactly as the shortcut does -- a preview
'     that refuses to start where the live app starts fine is a review cycle
'     lost to the launcher,
'   - it runs with THIS worktree as the working directory, so `-m promptcrafter`
'     resolves to the branch's code rather than the editable install that points
'     at the primary. That trap is documented in CLAUDE.md and it fails silently:
'     the app comes up, on main, looking like the branch works,
'   - it reads THIS worktree's schema.local.json, so the branch is judged on the
'     real schema. Copy the primary's in before handing the preview over; without
'     one the session falls back to the fabricated demo and shows three sections
'     of heroes and pigeons, which is not the thing under review.
' Named distinctly from the live app's shortcut on purpose: an identically named
' launcher once sent a whole review cycle against the old app while the fix sat
' unlaunched.

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

projectRoot = fso.GetParentFolderName(WScript.ScriptFullName)
launcherLog = projectRoot & "\promptcrafter-preview-launcher.log"

Function Quote(s)
  Quote = Chr(34) & s & Chr(34)
End Function

' <primary>\.claude\worktrees\<this worktree> -> up three levels to the primary.
primaryRoot = fso.GetParentFolderName(fso.GetParentFolderName(fso.GetParentFolderName(projectRoot)))

' The primary's venv when it has one, else whatever python the shortcut would
' have found. An empty or absent .venv is a normal state of the primary, so
' refusing to launch there would strand every preview behind a MsgBox for an
' interpreter the app never needed.
Function FindPythonCommand()
  Dim venvPython, candidates, i

  venvPython = primaryRoot & "\.venv\Scripts\pythonw.exe"
  If fso.FileExists(venvPython) Then
    FindPythonCommand = Quote(venvPython)
    Exit Function
  End If

  candidates = Array( _
    "pythonw", _
    "python", _
    "py -3" _
  )
  For i = 0 To UBound(candidates)
    If shell.Run("cmd /c where " & Split(candidates(i), " ")(0) & " >nul 2>nul", 0, True) = 0 Then
      FindPythonCommand = candidates(i)
      Exit Function
    End If
  Next
  FindPythonCommand = ""
End Function

pythonCmd = FindPythonCommand()
If pythonCmd = "" Then
  MsgBox "Could not find python or py launcher.", vbCritical, "PromptCrafter (branch preview)"
  WScript.Quit 1
End If

cmd = "cmd /c cd /d " & Quote(projectRoot) & " && " & pythonCmd & " -m promptcrafter 1>>" & Quote(launcherLog) & " 2>&1"
shell.Run cmd, 0, False
