$ErrorActionPreference = 'Stop'

$LauncherRoot = Split-Path -Parent $PSScriptRoot
$ShortcutPath = Join-Path $LauncherRoot 'PromptCrafter.lnk'
# This project's own interpreter, never the one on PATH. A shortcut is how
# Windows decides what a running process IS: it matches a process against a
# pinned shortcut whose target is the same executable, and draws that
# shortcut's icon and name for it. Pinned at the shared C:\PythonXXX\pythonw.exe,
# this shortcut lent PromptCrafter's mark to every unrelated Python process on
# the machine -- the tray apps, the broker's workers -- so the task list showed
# a column of PromptCrafter rows while PromptCrafter had not run in months.
# An interpreter inside this checkout is claimed by this app and nothing else.
$LauncherExe = Join-Path $LauncherRoot '.venv\Scripts\pythonw.exe'
$LauncherArgs = '-m promptcrafter'
$IconPath = Join-Path $LauncherRoot 'icon.ico'
$AppUserModelId = 'Local.PromptCrafter'

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Text;

[ComImport]
[Guid("00021401-0000-0000-C000-000000000046")]
class CShellLink {}

[ComImport]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("000214F9-0000-0000-C000-000000000046")]
interface IShellLinkW
{
    void GetPath([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder pszFile, int cch, IntPtr pfd, int fFlags);
    void GetIDList(out IntPtr ppidl);
    void SetIDList(IntPtr pidl);
    void GetDescription([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder pszName, int cch);
    void SetDescription([MarshalAs(UnmanagedType.LPWStr)] string pszName);
    void GetWorkingDirectory([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder pszDir, int cch);
    void SetWorkingDirectory([MarshalAs(UnmanagedType.LPWStr)] string pszDir);
    void GetArguments([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder pszArgs, int cch);
    void SetArguments([MarshalAs(UnmanagedType.LPWStr)] string pszArgs);
    void GetHotkey(out short pwHotkey);
    void SetHotkey(short wHotkey);
    void GetShowCmd(out int piShowCmd);
    void SetShowCmd(int iShowCmd);
    void GetIconLocation([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder pszIconPath, int cch, out int piIcon);
    void SetIconLocation([MarshalAs(UnmanagedType.LPWStr)] string pszIconPath, int iIcon);
    void SetRelativePath([MarshalAs(UnmanagedType.LPWStr)] string pszPathRel, int dwReserved);
    void Resolve(IntPtr hwnd, int fFlags);
    void SetPath([MarshalAs(UnmanagedType.LPWStr)] string pszFile);
}

[ComImport]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99")]
interface IPropertyStore
{
    void GetCount(out uint cProps);
    void GetAt(uint iProp, out PROPERTYKEY pkey);
    void GetValue(ref PROPERTYKEY key, out PROPVARIANT pv);
    void SetValue(ref PROPERTYKEY key, ref PROPVARIANT pv);
    void Commit();
}

[ComImport]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("0000010b-0000-0000-C000-000000000046")]
interface IPersistFile
{
    void GetClassID(out Guid pClassID);
    void IsDirty();
    void Load([MarshalAs(UnmanagedType.LPWStr)] string pszFileName, uint dwMode);
    void Save([MarshalAs(UnmanagedType.LPWStr)] string pszFileName, bool fRemember);
    void SaveCompleted([MarshalAs(UnmanagedType.LPWStr)] string pszFileName);
    void GetCurFile([MarshalAs(UnmanagedType.LPWStr)] out string ppszFileName);
}

[StructLayout(LayoutKind.Sequential, Pack = 4)]
struct PROPERTYKEY
{
    public Guid fmtid;
    public uint pid;
}

[StructLayout(LayoutKind.Explicit)]
struct PROPVARIANT
{
    [FieldOffset(0)] public ushort vt;
    [FieldOffset(8)] public IntPtr pointerValue;

    public static PROPVARIANT FromString(string value)
    {
        var pv = new PROPVARIANT();
        pv.vt = 31;
        pv.pointerValue = Marshal.StringToCoTaskMemUni(value);
        return pv;
    }

    public void Clear()
    {
        if (pointerValue != IntPtr.Zero)
        {
            Marshal.FreeCoTaskMem(pointerValue);
            pointerValue = IntPtr.Zero;
        }
    }
}

public static class ShortcutPropertyWriter
{
    public static void Write(string shortcutPath, string targetPath, string arguments, string workingDirectory, string iconPath, string appId, string displayName)
    {
        var appIdKey = new PROPERTYKEY
        {
            fmtid = new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3"),
            pid = 5
        };
        var relaunchDisplayNameKey = new PROPERTYKEY
        {
            fmtid = new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3"),
            pid = 4
        };
        var relaunchIconResourceKey = new PROPERTYKEY
        {
            fmtid = new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3"),
            pid = 3
        };

        var link = (IShellLinkW)new CShellLink();
        link.SetPath(targetPath);
        link.SetArguments(arguments);
        link.SetWorkingDirectory(workingDirectory);
        link.SetIconLocation(iconPath, 0);

        var store = (IPropertyStore)link;
        var persist = (IPersistFile)link;

        var appIdVar = PROPVARIANT.FromString(appId);
        var displayVar = PROPVARIANT.FromString(displayName);
        var iconVar = PROPVARIANT.FromString(iconPath + ",0");

        try
        {
            store.SetValue(ref appIdKey, ref appIdVar);
            store.SetValue(ref relaunchDisplayNameKey, ref displayVar);
            store.SetValue(ref relaunchIconResourceKey, ref iconVar);
            store.Commit();
            persist.Save(shortcutPath, true);
        }
        finally
        {
            appIdVar.Clear();
            displayVar.Clear();
            iconVar.Clear();
        }
    }
}
"@

if (-not (Test-Path -LiteralPath $LauncherExe)) {
  throw "No interpreter at $LauncherExe -- create the project venv first"
}

Remove-Item -LiteralPath $ShortcutPath -Force -ErrorAction SilentlyContinue
[ShortcutPropertyWriter]::Write($ShortcutPath, $LauncherExe, $LauncherArgs, $LauncherRoot, $IconPath, $AppUserModelId, 'PromptCrafter')

Write-Host "Updated shortcut: $ShortcutPath"
Write-Host "Target: $LauncherExe"
Write-Host "Arguments: $LauncherArgs"
