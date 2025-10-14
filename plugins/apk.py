async def apkan1_cmd(client, message):
    text = client.get_text(message)
    if not text:
        return await message.reply(
            f"**Please give word for search from https://an1.com/.\nExample: `{message.text.split()[0]} pou`**",
            disable_web_page_preview=True,
        )
    payload = {"search": text}
    url = "https://api.siputzx.my.id/api/apk/an1"
    response = await Tools.fetch.post(url, json=payload)
    if response.status_code != 200:
        return await message.reply(f"**Please try again later!!")
    data = response.json()["data"]
    if len(data) == 0:
        return await message.reply("<b>No apk found!!</b>")
    uniq = f"{str(uuid4())}"
    state.set(uniq.split("-")[0], uniq.split("-")[0], data)
    try:
        inline = await ButtonUtils.send_inline_bot_result(
            message,
            message.chat.id,
            bot.me.username,
            f"inline_apkan1 {uniq.split('-')[0]}",
        )
        if inline:
            return await message.delete()
    except Exception as er:
        return await message.reply(f"**ERROR**: {str(er)}")
