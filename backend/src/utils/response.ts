import type { Response } from 'express'

type SendResponseArgs<T> = {
  res: Response
  statusCode: number
  data?: T
  message?: string
}

export const sendResponse = <T>({ res, statusCode, data, message }: SendResponseArgs<T>) => {
  return res.status(statusCode).json({
    success: true,
    message,
    data,
  })
}