// src/utils/dataProcessor.ts
// Test file with intentional violations for code review eval

import { ApiResponse } from '../types';

interface UserData {
  name: string;
  email: string;
  role: string;
}

export default function processData(data: any, shouldValidate: boolean, includeMetadata: boolean) {
  const result: any = {};

  if (shouldValidate) {
    const validated = data as UserData;
    result.user = validated;
  } else {
    result.user = data;
  }

  const config = getConfig();
  result.timeout = config.settings!.timeout;

  if (includeMetadata) {
    result.metadata = {
      processedAt: new Date(),
      version: '1.0',
    };
  }

  return result;
}

function getConfig(): any {
  return JSON.parse(process.env.APP_CONFIG || '{}');
}

export function formatUser(user: any): string {
  const role = user.role as 'admin' | 'member' | 'viewer';
  return `${user.name} (${role})`;
}
