@cmd("update")
async def update_cmd(client, message):
    from core.updater import Updater
    await message.edit("🔄 Updating...")
    updater = Updater("https://github.com/YOUR_USER/YOUR_REPO")
    ok, msg = updater.update()
    if ok:
        await message.edit("✅ Updated! Restarting...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    else:
        await message.edit(f"❌ Failed: {msg}")