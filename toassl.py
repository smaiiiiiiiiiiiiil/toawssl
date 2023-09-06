token = "6696259497:AAEBaWKhEQQigvGl3E89aEUv-INL-R_tlyA"
ownerID = 6623446472

import asyncio 
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from kvsqlite.sync import Client as DB
from datetime import date
from pyrogram.errors import FloodWait 
botdb = DB('botdb.sqlite')
msgsdb = DB('msgsdb.sqlite')

bot = Client(
  'support'+token.split(":")[0],
  9398500, 
  'ad2977d673006bed6e5007d953301e13',
  bot_token=token, in_memory=True
)
bot.start()
mention = (bot.get_users(ownerID)).mention



bot.set_bot_commands([
    BotCommand("start", "لبدء الدردشة"),
    BotCommand("lang", "لتغير الغة")]
)

STARTKEY = InlineKeyboardMarkup(
        [
          [
            InlineKeyboardButton("⟨ الإذاعة ⟩", callback_data="broadcast")
          ],
          [
            InlineKeyboardButton("⟨ الاعضاء ⟩", callback_data="stats"),
            InlineKeyboardButton("⟨ الأدمنية ⟩", callback_data="adminstats"),
            InlineKeyboardButton("⟨ banned ⟩", callback_data="bannedstats"),
          ],
          [
            InlineKeyboardButton("⟨ Whois ⟩",callback_data="whois"),
            InlineKeyboardButton("⟨ ban ⟩",callback_data="ban"),
          ],
          [
            InlineKeyboardButton("⟨ ban ⟩",callback_data="ban"),
          ],
          [
            InlineKeyboardButton("⟨ Promote ⟩",callback_data="addadmin"),
            InlineKeyboardButton("⟨ Demote ⟩",callback_data="remadmin"),
          ]
        ]
      )
if not botdb.get("db"+token.split(":")[0]):
    data = {
      "users":[],
      "admins":[],
      "banned":[],
    }
    botdb.set("db"+token.split(":")[0], data)

if not ownerID in botdb.get("db"+token.split(":")[0])["admins"]:
    data = botdb.get("db"+token.split(":")[0])
    data["admins"].append(ownerID)
    botdb.set("db"+token.split(":")[0], data)

@bot.on_message(filters.command("start") & filters.private)
async def on_start(c,m):
    getDB = botdb.get("db"+token.split(":")[0])
    if m.from_user.id in getDB["banned"]:
      return await m.reply("🚫 أنت ممنوع من استخدام هذا الروبوت",quote=True)
    if m.from_user.id == ownerID:     
      await m.reply(f"**• مرحبا {m.from_user.mention}",reply_markup=STARTKEY,quote=True)
    else:
      text = f"• اهلا ⌯ {m.from_user.mention}\n• مرحبا بك  رسالتك."
      await m.reply(text,quote=True)
    if not m.from_user.id in getDB["users"]:
      data = getDB
      data["users"].append(m.from_user.id)
      botdb.set("db"+token.split(":")[0], data)
      for admin in data["admins"]:
          text = f"– New user stats the bot :"
          username = "@"+m.from_user.username if m.from_user.username else "None"
          text += f"\n\n𖡋 𝐔𝐒𝐄 ⌯  {username}"
          text += f"\n𖡋 𝐍𝐀𝐌𝐄 ⌯  {m.from_user.mention}"
          text += f"\n𖡋 𝐈𝐃 ⌯  `{m.from_user.id}`"
          text += f"\n𖡋 𝐃𝐀𝐓𝐄 ⌯  **{date.today()}**"
          try: await c.send_message(admin, text, reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton (m.from_user.first_name,user_id=m.from_user.id)]]))
          except: pass
    data = {"name":m.from_user.first_name[:25], "username":m.from_user.username, "mention":m.from_user.mention(m.from_user.first_name[:25]),"id":m.from_user.id}
    botdb.set(f"USER:{m.from_user.id}",data)

@bot.on_message(filters.command(["lang","language"]) & filters.private)
async def onLang(c,m):
   keyboard=InlineKeyboardMarkup (
         [
           [
             InlineKeyboardButton ("English 🇬🇧",callback_data="english"),
             InlineKeyboardButton ("Arabic 🇵🇸", callback_data="arabic"),
           ]
         ]
       )
   await m.reply(f"**– Welcome, please choose your language\n\n- مرحباً ، يرجى اختيار لغتك**", reply_markup=keyboard)

@bot.on_message(filters.private & ~filters.service)
async def on_messages(c,m):
    if m.from_user.id != ownerID and m.from_user.id not in botdb.get("db"+token.split(":")[0])["admins"]:
      if m.from_user.id in botdb.get("db"+token.split(":")[0])["banned"]:
          return await m.reply("🚫 You are banned from using this bot",quote=True)
      else:
        await m.reply(f"– لقد تلقينا رسالتك وسوف نقوم بالرد في أسرع وقت ممكن.",quote=True)
        for admin in botdb.get("db"+token.split(":")[0])["admins"]:
          try:
            forward=await m.forward(admin)
            msgsdb.set(f"MSG:{forward.id}:{admin}",{"id":m.from_user.id,"msgID":m.id})
          except FloodWait as x:
            await asyncio.sleep(x.value)
          except Exception:
            pass

    if (m.from_user.id == ownerID or m.from_user.id in botdb.get("db"+token.split(":")[0])["admins"]) and m.reply_to_message and m.reply_to_message.forward and msgsdb.get(f"MSG:{m.reply_to_message.id}:{m.from_user.id}"):
      getMSG = msgsdb.get(f"MSG:{m.reply_to_message.id}:{m.from_user.id}")
      msgID = getMSG["msgID"]
      userID = getMSG["id"]
      try:
        await m.copy(userID, reply_to_message_id=msgID)
        getUser=botdb.get(f"USER:{userID}")
        await m.reply(f"• تم إرسال رسالتك إلى ⌯ {getUser['mention']}",quote=True)
      except FloodWait as x:
        await asyncio.sleep(x.value)
      except Exception as e:
        await m.reply(f"`{e}`",quote=True)

    if botdb.get(f"broad:{m.from_user.id}") and m.from_user.id == ownerID:
      botdb.delete(f"broad:{m.from_user.id}")
      botdb.delete(f"whois:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"add:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"rem:{m.from_user.id}")
      text = "**— Wait .. **\n"
      reply = await m.reply(text,quote=True)
      count=0
      users=botdb.get("db"+token.split(":")[0])["users"]
      for user in users:
        try:
          await m.copy(user)
          count+=1
          await reply.edit(text+f"**— The msg was sent for [ {count}/{len(users)} ] user**")
        except FloodWait as x:
          await asyncio.sleep(x.value)
        except Exception:
          pass
      return True

    if m.text and botdb.get(f"whois:{m.from_user.id}") and m.from_user.id == ownerID:
      botdb.delete(f"broad:{m.from_user.id}")
      botdb.delete(f"whois:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"add:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"rem:{m.from_user.id}")
      getUser=botdb.get(f"USER:{m.text[:15]}")
      if not getUser:
        return await m.reply("– ID Not Found",quote=True)
      else:
          name=getUser["name"]
          id=getUser["id"]
          mention=getUser["mention"]
          username="@"+getUser["username"] if getUser["username"] else "None"
          language=botdb.get(f"LANG:{id}")
          text = f"𖡋 𝐔𝐒𝐄 ⌯  {username}"
          text += f"\n𖡋 𝐍𝐀𝐌𝐄 ⌯  {name}"
          text += f"\n𖡋 𝐈𝐃 ⌯  `{id}`"
          text += f"\n𖡋 𝑳𝐀𝐍𝐆 ⌯  {language}"
          text += f"\n𖡋 𝐀𝐂𝐂 𝑳𝐈𝐍𝐊 ⌯  **{mention}**"
          return await m.reply(text,quote=True)

    if m.text and botdb.get(f"ban:{m.from_user.id}") and m.from_user.id == ownerID:
      botdb.delete(f"broad:{m.from_user.id}")
      botdb.delete(f"whois:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"add:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"rem:{m.from_user.id}")
      getUser=botdb.get(f"USER:{m.text[:15]}")
      if not getUser:
        return await m.reply("– ID Not Found",quote=True)
      else:
        if getUser["id"] in botdb.get("db"+token.split(":")[0])["admins"]:
          return await m.reply(f"– You cant ban ⌯ {getUser['mention']} ⌯ لأنه ليس مشرف",quote=True)
        else:
          if getUser["id"] in botdb.get("db"+token.split(":")[0])["banned"]:
            return await m.reply(f"– You cant ban ⌯ {getUser['mention']} ⌯ bcuz he is already banned",quote=True)
          name=getUser["mention"]
          id=getUser["id"]
          username="@"+getUser["username"] if getUser["username"] else "None"
          language=botdb.get(f"LANG:{id}")
          text = f"- this user added to blacklist:\n\n"
          text += f"𖡋 𝐔𝐒𝐄 ⌯  {username}"
          text += f"\n𖡋 𝐍𝐀𝐌𝐄 ⌯  {name}"
          text += f"\n𖡋 𝑳𝐀𝐍𝐆 ⌯  {language}"
          text += f"\n𖡋 𝐈𝐃 ⌯  `{id}`"
          data = botdb.get("db"+token.split(":")[0])
          data["banned"].append(id)
          botdb.set("db"+token.split(":")[0],data)
          return await m.reply(text,quote=True)
    if m.text and botdb.get(f"ban:{m.from_user.id}") and m.from_user.id == ownerID:
      botdb.delete(f"broad:{m.from_user.id}")
      botdb.delete(f"whois:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"add:{m.from_user.id}")
      botdb.delete(f"rem:{m.from_user.id}")
      getUser=botdb.get(f"USER:{m.text[:15]}")
      if not getUser:
        return await m.reply("– ID Not Found",quote=True)
      else:
        if getUser["id"] in botdb.get("db"+token.split(":")[0])["admins"]:
          return await m.reply(f"– لايمكنك حظره ⌯ {getUser['mention']} ⌯ لأنه ليس مشرف" ,quote=True)
        else:
          if not getUser["id"] in botdb.get("db"+token.split(":")[0])["banned"]:
            return await m.reply(f"–لايمكنك حظره ⌯ {getUser['mention']} ⌯ لأنه ليس مشرف",quote=True)
          name=getUser["mention"]
          id=getUser["id"]
          username="@"+getUser["username"] if getUser["username"] else "None"
          language=botdb.get(f"LANG:{id}")
          text = f"- تم حذف هذا المستخدم من القائمة السوداء:\n\n"
          text += f"𖡋 𝐔𝐒𝐄 ⌯  {username}"
          text += f"\n𖡋 𝐍𝐀𝐌𝐄 ⌯  {name}"
          text += f"\n𖡋 𝑳𝐀𝐍𝐆 ⌯  {language}"
          text += f"\n𖡋 𝐈𝐃 ⌯  `{id}`"
          data = botdb.get("db"+token.split(":")[0])
          data["banned"].remove(id)
          botdb.set("db"+token.split(":")[0],data)
          return await m.reply(text,quote=True)

    if m.text and botdb.get(f"add:{m.from_user.id}") and m.from_user.id == ownerID:
      botdb.delete(f"broad:{m.from_user.id}")
      botdb.delete(f"whois:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"add:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"rem:{m.from_user.id}")
      getUser=botdb.get(f"USER:{m.text[:15]}")
      if not getUser:
        return await m.reply("– ID Not Found",quote=True)
      else:
        if getUser["id"] in botdb.get("db"+token.split(":")[0])["admins"]:
          return await m.reply(f"⌯ {getUser['mention']} ⌯ Already in admins",quote=True)
        else:
          if getUser["id"] in botdb.get("db"+token.split(":")[0])["banned"]:
            return await m.reply(f"– You cant promote ⌯ {getUser['mention']} ⌯ bcuz he is an banned user",quote=True)
          name=getUser["mention"]
          id=getUser["id"]
          username="@"+getUser["username"] if getUser["username"] else "None"
          language=botdb.get(f"LANG:{id}")
          text = f"- this user added to admins list:\n\n"
          text += f"𖡋 𝐔𝐒𝐄 ⌯  {username}"
          text += f"\n𖡋 𝐍𝐀𝐌𝐄 ⌯  {name}"
          text += f"\n𖡋 𝑳𝐀𝐍𝐆 ⌯  {language}"
          text += f"\n𖡋 𝐈𝐃 ⌯  `{id}`"
          data = botdb.get("db"+token.split(":")[0])
          data["admins"].append(id)
          botdb.set("db"+token.split(":")[0],data)
          return await m.reply(text,quote=True)

    if m.text and botdb.get(f"rem:{m.from_user.id}") and m.from_user.id == ownerID:
      botdb.delete(f"broad:{m.from_user.id}")
      botdb.delete(f"whois:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"add:{m.from_user.id}")
      botdb.delete(f"rem:{m.from_user.id}")
      getUser=botdb.get(f"USER:{m.text[:15]}")
      if not getUser:
        return await m.reply("– ID Not Found",quote=True)
      else:
        if not getUser["id"] in botdb.get("db"+token.split(":")[0])["admins"]:
          return await m.reply(f"⌯ {getUser['mention']} ⌯ Not admin",quote=True)
        else:
          name=getUser["mention"]
          id=getUser["id"]
          username="@"+getUser["username"] if getUser["username"] else "None"
          language=botdb.get(f"LANG:{id}")
          text = f"- this user deleted from admins list:\n\n"
          text += f"𖡋 𝐔𝐒𝐄 ⌯  {username}"
          text += f"\n𖡋 𝐍𝐀𝐌𝐄 ⌯  {name}"
          text += f"\n𖡋 𝑳𝐀𝐍𝐆 ⌯  {language}"
          text += f"\n𖡋 𝐈𝐃 ⌯  `{id}`"
          data = botdb.get("db"+token.split(":")[0])
          data["admins"].remove(id)
          botdb.set("db"+token.split(":")[0],data)
          return await m.reply(text,quote=True)

@bot.on_callback_query()
async def on_Callback(c,m):

     if m.data == "english":
       await m.answer("English language selected successfully",show_alert=True)
       botdb.set(f"LANG:{m.from_user.id}","english")
       await m.message.delete()
      
     if m.data == "arabic":
       await m.answer("تم اختيار اللغة العربية بنجاح",show_alert=True)
       botdb.set(f"LANG:{m.from_user.id}","arabic")
       await m.message.delete()
      
     if m.data == "broadcast" and m.from_user.id == ownerID:
      await m.edit_message_text("• Send the broadcast now",reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ("back",callback_data="back")]]))
      botdb.set(f"broad:{m.from_user.id}",True)
      botdb.delete(f"whois:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"add:{m.from_user.id}")
      botdb.delete(f"rem:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      
     if m.data == "whois" and m.from_user.id == ownerID:
      await m.edit_message_text("• Send the ID now",reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ("back",callback_data="back")]]))
      botdb.set(f"whois:{m.from_user.id}",True)
      botdb.delete(f"broad:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"add:{m.from_user.id}")
      botdb.delete(f"rem:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      
     if m.data == "ban" and m.from_user.id == ownerID:
      await m.edit_message_text("• Send the ID now",reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ("back",callback_data="back")]]))
      botdb.set(f"ban:{m.from_user.id}",True)
      botdb.delete(f"broad:{m.from_user.id}")
      botdb.delete(f"whois:{m.from_user.id}")
      botdb.delete(f"add:{m.from_user.id}")
      botdb.delete(f"rem:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")

     if m.data == "ban" and m.from_user.id == ownerID:
      await m.edit_message_text("• Send the ID now",reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ("back",callback_data="back")]]))
      botdb.set(f"ban:{m.from_user.id}",True)
      botdb.delete(f"broad:{m.from_user.id}")
      botdb.delete(f"whois:{m.from_user.id}")
      botdb.delete(f"add:{m.from_user.id}")
      botdb.delete(f"rem:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")

     if m.data == "addadmin" and m.from_user.id == ownerID:
      await m.edit_message_text("• Send the ID now",reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ("back",callback_data="back")]]))
      botdb.set(f"add:{m.from_user.id}",True)
      botdb.delete(f"broad:{m.from_user.id}")
      botdb.delete(f"whois:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"rem:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")

     if m.data == "remadmin" and m.from_user.id == ownerID:
      await m.edit_message_text("• Send the ID now",reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ("back",callback_data="back")]]))
      botdb.set(f"rem:{m.from_user.id}",True)
      botdb.delete(f"broad:{m.from_user.id}")
      botdb.delete(f"whois:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"add:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")

     if m.data == "back" and m.from_user.id == ownerID:
      await m.answer("• تم الرجوع بنجاح والغاء كل شي ",show_alert=True)
      await m.edit_message_text(f"**• مرحبا ⌯ {m.from_user.mention}**",reply_markup=STARTKEY)
      botdb.delete(f"broad:{m.from_user.id}")
      botdb.delete(f"whois:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      botdb.delete(f"add:{m.from_user.id}")
      botdb.delete(f"rem:{m.from_user.id}")
      botdb.delete(f"ban:{m.from_user.id}")
      
     if m.data == "stats" and m.from_user.id == ownerID:
      users = len(botdb.get("db"+token.split(":")[0])["users"])
      await m.answer(f"• Users stats ⌯ {users}", show_alert=True,cache_time=10)
      
     if m.data == "adminstats" and m.from_user.id == ownerID:
      admins = len(botdb.get("db"+token.split(":")[0])["admins"])
      await m.answer(f"• admins stats⌯ {admins}", show_alert=True,cache_time=60)
      text = "- admins:\n\n"
      count = 1
      for admin in botdb.get("db"+token.split(":")[0])["admins"]:
          if count==101: break
          getUser = botdb.get(f"USER:{admin}")
          mention=getUser["mention"]
          id=getUser["id"]
          text += f"{count}) {mention} ~ (`{id}`)\n"
          count+=1
      text+="\n\n—"
      await m.message.reply(text,quote=True)
  
     if m.data == "bannedstats" and m.from_user.id == ownerID:
      bans = botdb.get("db"+token.split(":")[0])["banned"]
      if not bans:  return await m.answer("• bannedlist empty", show_alert=True,cache_time=60)
      await m.answer(f"• banned stats ⌯ {len(bans)}", show_alert=True,cache_time=60)
      text = "- banned Users:\n\n"
      count = 1
      for banned in bans:
          if count==101: break
          getUser = botdb.get(f"USER:{banned}")
          mention=getUser["mention"]
          id=getUser["id"]
          text += f"{count}) {mention} ~ (`{id}`)\n"
          count+=1
      text+="\n\n—"
      await m.message.reply(text,quote=True)

print("ur bot started successfully")
idle()

