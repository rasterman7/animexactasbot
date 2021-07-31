import logging
from pony.orm import *
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import CallbackContext, ConversationHandler
from usecases.polls.sugerir_opcion import polls, store_option

NOMBRE, LINK = range(2)

logger = logging.getLogger('animexactasbot.log')


def polls_reply(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    callback_args = query.data.split("|")
    
    poll_name = callback_args[1]
    context.user_data['poll_id'] = callback_args[2]
    
    query.message.reply_text(
        f'Elegiste el poll de {poll_name}.\n\n'
        '¿Cuál es el nombre de la sugerencia?'
    )
    
    try:
        query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([]))
    except:
        pass

    return

def aux_create_option_button(poll):
    return InlineKeyboardButton(text=f"{p.text}", callback_data=f"polls_reply|{p.text}|{p.id}")

def sugerir_opcion(update: Update, context: CallbackContext):
    ps = polls();
    columns = 3
    botones = []
    for k in range(0, len(ps), columns):
        row = [aux_create_option_button(p) for p in ps[k:k + columns] ] #TODO: make a function out of this
        botones.append(row)
    reply_markup = InlineKeyboardMarkup(botones)
    update.message.reply_text(
        "De que poll queres sugerir una opción?\n\n"
        "Si queres cancelar la operacion, podes escribir el comando /cancelar",
        reply_markup=reply_markup
    )

    return NOMBRE


def nombre(update: Update, context: CallbackContext) -> int:
    context.user_data["nombre_opcion"] = update.message.text

    update.message.reply_text(
        "Genial! Ahora pasame un link (Youtube, Vimeo, MAL, IMDb, etc)."
    )

    return LINK


def link(update: Update, context: CallbackContext) -> int:
    context.user_data['link'] = update.message.text

    store_option(context.user_data)

    update.message.reply_text(
        # "Tu sugerencia fue añadida correctamente y esta pendiente de ser aprobada."
        f"Tu sugerencia fue añadida al poll correctamente y aparecerá entre las opciones a rankear.\n\n"
        f"Felicitaciones Dante!!"
    )

    return ConversationHandler.END


def cancelar(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Cancelaste la operación.\n\n"
        "Volvé a ingresar un comando para iniciar una nueva operación."
    )

    return ConversationHandler.END
